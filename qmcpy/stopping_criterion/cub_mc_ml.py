from ._stopping_criterion import StoppingCriterion
from ..accumulate_data import MLMCData
from ..discrete_distribution import IIDStdGaussian
from ..true_measure import Gaussian
from ..integrand import MLCallOptions
from ..util import MaxSamplesWarning, ParameterError, MaxLevelsWarning
from numpy import ceil, sqrt, arange, minimum, maximum, hstack, zeros
from scipy.stats import norm
from time import time
import warnings


class CubMCML(StoppingCriterion):
    """
    Stopping criterion based on multi-level monte carlo.
    
    >>> mlco = MLCallOptions(Gaussian(IIDStdGaussian(seed=7)))
    >>> sc = CubMCML(mlco,abs_tol=.05)
    >>> solution,data = sc.integrate()
    >>> solution
    10.443836668379447
    >>> data
    Solution: 10.4438        
    MLCallOptions (Integrand Object)
        option          european
        sigma           0.200
        k               100
        r               0.050
        t               1
        b               85
    IIDStdGaussian (DiscreteDistribution Object)
        dimension       2^(6)
        seed            7
        mimics          StdGaussian
    Gaussian (TrueMeasure Object)
        mean            0
        covariance      1
    CubMCML (StoppingCriterion Object)
        rmse_tol        0.019
        n_init          2^(8)
        levels_min      2^(1)
        levels_max      10
        theta           2^(-2)
    MLMCData (AccumulateData Object)
        levels          6
        n_level         [7.817e+05 1.531e+04 6.633e+03 2.078e+03 7.560e+02 2.730e+02 1.180e+02]
        mean_level      [1.006e+01 1.844e-01 1.014e-01 5.129e-02 2.472e-02 1.341e-02 8.233e-03]
        var_level       [1.963e+02 1.505e-01 4.124e-02 1.110e-02 2.901e-03 7.013e-04 2.446e-04]
        cost_per_sample [ 1.  2.  4.  8. 16. 32. 64.]
        alpha           0.921
        beta            1.883
        gamma           1.000
        time_integrate  ...

    Adapted from
        http://people.maths.ox.ac.uk/~gilesm/mlmc/#MATLAB

    Reference:
        M.B. Giles. 'Multi-level Monte Carlo path simulation'. 
        Operations Research, 56(3):607-617, 2008.
        http://people.maths.ox.ac.uk/~gilesm/files/OPRE_2008.pdf.
    """

    parameters = ['rmse_tol','n_init','levels_min','levels_max','theta']

    def __init__(self, integrand, abs_tol=.05, alpha=.01, rmse_tol=None, n_init=256., n_max=1e10, 
        levels_min=2., levels_max=10., alpha0=-1., beta0=-1., gamma0=-1.):
        """
        Args:
            integrand (Integrand): integrand with multi-level g method
            rmse_tol (float): desired accuracy (rms error) > 0 
            n_init (int): initial number of samples
            n_max (int): maximum number of samples
            levels_min (int): minimum level of refinement >= 2
            levels_max (int): maximum level of refinement >= Lmin
            alpha0 (float): weak error is O(2^{-alpha0*level})
            beta0 (float): variance is O(2^{-bet0a*level})
            gamma0 (float): sample cost is O(2^{gamma0*level})
        Note:
            if alpha, beta, gamma are not positive, then they will be estimated
        """
        if levels_min < 2:
            raise ParameterError('needs levels_min >= 2')
        if levels_max < levels_min:
            raise ParameterError('needs levels_max >= levels_min')
        if n_init <= 0:
            raise ParameterError('needs n_init > 0')
        # initialization
        self.rmse_tol = float(rmse_tol) if rmse_tol else (float(abs_tol) / norm.ppf(1-alpha/2.))
        self.n_init = float(n_init)
        self.n_max = float(n_max)
        self.levels_min = float(levels_min)
        self.levels_max = float(levels_max)
        self.theta = 0.25
        # Verify Compliant Construction
        distribution = integrand.measure.distribution
        allowed_levels = 'multi'
        allowed_distribs = ["IIDStdUniform", "IIDStdGaussian", "CustomIIDDistribution"]
        super(CubMCML,self).__init__(distribution, allowed_levels, allowed_distribs)
        # Construct AccumulateData Object to House Integration Data
        self.data = MLMCData(self, integrand, self.levels_min, self.n_init, alpha0, beta0, gamma0)
    
    def integrate(self):
        """ See abstract method. """
        t_start = time()
        while self.data.diff_n_level.sum() > 0:
            self.data.update_data()
            self.data.n_total += self.data.diff_n_level.sum()
            # set optimal number of additional samples
            n_samples = self._get_next_samples()
            self.data.diff_n_level = maximum(0, n_samples-self.data.n_level)
            # if (almost) converged, estimate remaining error and decide 
            # whether a new level is required
            if (self.data.diff_n_level > 0.01*self.data.n_level).sum() == 0:
                range_ = arange(minimum(2.,self.data.levels-1)+1)
                idx = (self.data.levels-range_).astype(int)
                rem = (self.data.mean_level[idx] / 
                        2.**(range_*self.data.alpha)).max() / (2.**self.data.alpha - 1)
                # rem = ml(l+1) / (2^alpha - 1)
                if rem > sqrt(self.theta)*self.rmse_tol:
                    if self.data.levels == self.levels_max:
                        warnings.warn(
                            'Failed to achieve weak convergence. levels == levels_max.',
                            MaxLevelsWarning)
                    else:
                        self.data.levels += 1
                        self.data.var_level = hstack((self.data.var_level,
                            self.data.var_level[-1] / 2**self.data.beta))
                        self.data.cost_per_sample = hstack((self.data.cost_per_sample, 
                            self.data.cost_per_sample[-1] * 2**self.data.gamma))
                        self.data.n_level = hstack((self.data.n_level, 0.))
                        self.data.sum_level = hstack((self.data.sum_level,
                            zeros((2,1))))
                        self.data.cost_level = hstack((self.data.cost_level, 0.))
                        n_samples = self._get_next_samples()
                        self.data.diff_n_level = maximum(0., n_samples-self.data.n_level)
            # check if over sample budget
            if (self.data.n_total + self.data.diff_n_level.sum()) > self.n_max:
                warning_s = """
                Alread generated %d samples.
                Trying to generate %d new samples, which would exceed n_max = %d.
                Stopping integration process.
                Note that error tolerances may no longer be satisfied""" \
                % (int(self.data.n_total), int(self.data.diff_n_level.sum()), int(self.n_max))
                warnings.warn(warning_s, MaxSamplesWarning)
                break
            # finally, evaluate multilevel estimator
        self.data.solution = (self.data.sum_level[0,:]/self.data.n_level).sum()
        self.data.time_integrate = time() - t_start
        return self.data.solution,self.data
    
    def _get_next_samples(self):
        ns = ceil( sqrt(self.data.var_level/self.data.cost_per_sample) * 
                sqrt(self.data.var_level*self.data.cost_per_sample).sum() / 
                ((1-self.theta)*self.rmse_tol**2) )
        return ns