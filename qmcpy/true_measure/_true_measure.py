from ..util import MethodImplementationError, _univ_repr, DimensionError


class TrueMeasure(object):
    """ True Measure abstract class. DO NOT INSTANTIATE. """

    def __init__(self):
        prefix = 'A concrete implementation of TrueMeasure must have '
        if not hasattr(self, 'distribution'):
            raise ParameterError(prefix + 'self.distribution (a DiscreteDistribution instance)')
        if not hasattr(self,'parameters'):
            self.parameters = []
        self.dimension = self.distribution.dimension

    def gen_samples(self, *args, **kwargs):
        """
        ABSTRACT METHOD to generate samples from the DiscreteDistribution object
        and transform them to mimic TrueMeasure samples. 
        
        Args:
            *args (tuple): Ordered arguments to self.distribution.gen_samples
            **kwrags (dict): Keyword arguments to self.distribution.gen_samples
        
        Returns:
            ndarray: samples from the DiscreteDistribution transformed to mimic the TrueMeasure.
        
        Note:
            May not be applicable for all measures (ex: Lebesgue). 
        """
        raise MethodImplementationError(self,'gen_samples')
    
    def _transform_g_to_f(self, g):
        """
        ABSTRACT METHOD to transform g, the origianl integrand, to f,
        the integrand transformed to accept samples from the discrete distribution.  
        
        Args:
            g (method): original integrand (Integrand.g)
        
        Returns:
            function handle: transformed integrand
        """
        raise MethodImplementationError(self,'_transform_g_to_f')

    def set_dimension(self, dimension):
        """
        ABSTRACT METHOD to reset the dimension of the problem. 
        A wrapper around DiscreteDistribution.set_dimension.

        Args:
            dimension (int): new dimension to reset to 
        
        Note:
            May not be applicable for all measures (ex: Gaussian with covariance != k*eye(d) for scalar k)
        """
        raise DimensionError("Cannot reset dimension of %s object"%str(type(self).__name__))

    def pdf(self, x):
        """
        Probability density function

        Args:
            x (ndarray): d (dimension) vector sample at which to evaluate the pdf
        
        Note:
            May not be applicable for all measures (ex: Lebesgue).
        """ 
        raise MethodImplementationError(self,'pdf')

    def __repr__(self):
        return _univ_repr(self, "TrueMeasure", self.parameters)
    
    def plot(self, *args, **kwargs):
        """ Create a plot relevant to the true measure object. """
        raise MethodImplementationError(self,'plot')
