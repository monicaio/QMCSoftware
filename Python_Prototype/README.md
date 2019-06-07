<center>

# Quasi-Monte Carlo Community Software
</center>

## Overview
Quasi-Monte Carlo (QMC) methods are used to approximate multivariate integrals. They have four main components: an integrand, a discrete distribution, summary output data, and stoppingcriterion. Information about the integrand is obtained as a sequence of values of the function sampled at the data-sites of the discrete distribution. The stopping criterion tells the algorithm when the user-specified error tolerance has been satisfied. We are developing a framework that allows collaborators in the QMC community to develop plug-and-play modules in an effort to produce more efficient and portable QMC software. Each of the above four components is an abstract class. Abstract classes specify the common properties and methods of all subclasses. The ways in which the four kinds of classes interact with each other are also specified. Subclasses then flesh out different integrands, sampling schemes, and stopping criteria. Besides providing developers a way to link their new ideas with those implemented by the rest of the QMC community, we also aim to provide practitioners with state-of-the-art QMC software for their applications.</p>
<hr>

## Integrand Class (fun.m/.py)
<b>Summary:</b> The function to integrate<br>
<b>Concrete Classes:</b>
- Keister (KeisterFun.m/.py)
- Asian Call (AsianCallFun.m/.py)

<hr>

## Discrete Distribution Class (discreteDistribution.m/.py)
<b>Summary:</b> The distribution dictating sampling points of the function <br>
<b>Concrete Classes:</b>
- Independent Identically Distributed (IIDDistribution.m/py)

<hr>

## Output Data Class (accumData.m/.py)
<b>Summary:</b> The data values to track throughout the integration<br>
<b>Concrete Classes:</b>
- Mean Variance (meanVarData.m/.py)

<hr>

## Stopping Criterion Class (stoppingCriterion.m/.py)
<b>Summary:</b> The stopping criterion to determine sufficient approximation<br>
<b>Concrete Classes:</b>
- Centeral Limint Theorem (CLTStopping.m/py)

<hr>   

## Measure Class (measure.m/.py)
<b>Summary:</b> Specifies the components of a general measure used to define an integration problem or a sampling method<br>
<b>Available Measures:</b>
- stdUniform
- stdGaussian
- IIDZMeanGaussian
- BrownianMotion

<hr>

## Integration Method (integrate.py)
<b>Summary:</b> Preforms integration given Function's', Distribution, Data, and a Stopping Crition 

<hr>

## Credit
This package was originally developed in MATLAB by Fred Hickernell<br>
Translated to Python by Sou-Cheng T. Choi and Aleksei Sorokin


