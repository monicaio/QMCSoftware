import unittest

from algorithms.stop import DistributionCompatibilityError
from algorithms.stop.clt_rep import CLTRep
from algorithms.distribution.iid_distribution import IIDDistribution
from algorithms.measures.measures import StdUniform

class Test_CLTRep(unittest.TestCase):

    def test_Incompatible_Distrib(self):
        self.assertRaises(DistributionCompatibilityError,CLTRep,IIDDistribution(StdUniform([2])))

    def test_max_samples_warning(self):
        pass

if __name__ == "__main__":
    unittest.main()