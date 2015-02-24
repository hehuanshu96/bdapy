# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Simple Logistic Regression #
# 
# Here, we consider simple logistic regression which has only one covariate variable.  Let $x_1, x_2, \ldots, x_n$ be the covariate variable, $n_i$ be the number of trials in observation $i$, and $y_i$ be the number of "success".  The likelihood function can be written:
# $$
# p(y_i \mid \theta_1, \theta_2, n_i, x_i) \propto 
# [\text{logit}^{-1}(\theta_1 + \theta_2 x_i)]^{y_i}
# [1 - \text{logit}^{-1}(\theta_1 + \theta_2 x_i)]^{n_i - y_i}
# $$
# For simplicity, uniform prior is assumed on $\theta_1, \theta_2$.

# <markdowncell>

# ## Sampling from Grid (BDA 3.7) ##
# 
# Since parameters are only two-dimensional, we can afford to approximate the posterior distribution on grid points.

# <codecell>

% pylab inline
import numpy as np

# <markdowncell>

# First of all, here is the data we will use, from Racine et al. (1986).

# <codecell>

# Data from Racine et al. (1986) 
from pandas import *
bioassay_df = DataFrame({'dose':[-0.86,-0.30,-0.05,0.73],
                         'animals':[5,5,5,5],
                         'deaths':[0,1,3,5]
                         })

# <markdowncell>

# To produce Figure 3.3 (a), we define a function that evaluates log-posterior function.

# <codecell>

def log_posterior_helper(theta_1, theta_2, trials, successes, covariates, log_prior = lambda t1, t2: 0):
    ret = log_prior(theta_1, theta_2)
    # first compute prediction scores
    scores = theta_1 + theta_2 * covariates
    # then convert it to log-likelihood
    ret += np.sum(-np.log(1 + exp(-scores)) * successes - np.log(1 + exp(scores)) * (trials - successes ))
    return ret
log_posterior = \
    np.vectorize(log_posterior_helper, otypes=[np.float], excluded=[2,3,4,5])

# <codecell>

import pylab as pl
grid_num = 64
theta1_min = -4
theta1_max = 10
theta2_min = -10
theta2_max = 40
x = np.linspace(theta1_min, theta1_max, grid_num)
y = np.linspace(theta2_min, theta2_max, grid_num)
X, Y = np.meshgrid(x, y)
log_Z = log_posterior(X,Y,bioassay_df.animals, bioassay_df.deaths, bioassay_df.dose)
max_log_Z = log_Z.max()
Z = np.exp(log_Z - max_log_Z) * np.exp(max_log_Z)
levels=np.exp(max_log_Z) * np.linspace(0.05, 0.95, 10)
pl.axes().set_aspect(float(theta1_max-theta1_min)/(theta2_max-theta2_min))
pl.contourf(X, Y, Z, 8, alpha=.75, cmap='jet', 
            levels=np.exp(max_log_Z) * np.concatenate(([0], np.linspace(0.05, 0.95, 10), [1])))
pl.contour(X, Y, Z, 8, colors='black', linewidth=.5, levels=levels)
pl.axes().set_xlabel(r'$\theta_1$')
pl.axes().set_ylabel(r'$\theta_2$')

# <markdowncell>

# Above is Figure 3.3 (a).  Since the grid is given, sampling from it is trivial.

# <codecell>

# seed the RNG
np.random.seed(135791)
# normalize the grid
probs = np.ravel(Z)/np.sum(Z)
# sample from the normalized distribution
throws = np.random.choice(len(probs), 1000, p=probs)
theta1s = x[throws % grid_num]
theta2s = y[throws / grid_num]
xgrid_size = float(theta1_max-theta1_min)/(grid_num-1)
ygrid_size = float(theta2_max-theta2_min)/(grid_num-1)
# add jittering
theta1s += np.random.random(len(theta1s)) * xgrid_size - 0.5 * xgrid_size
theta2s += np.random.random(len(theta2s)) * ygrid_size - 0.5 * ygrid_size
pl.scatter(theta1s, theta2s, marker='.', s=1)
pl.xlim(theta1_min, theta1_max)
pl.ylim(theta2_min, theta2_max)
pl.axes().set_aspect(float(theta1_max-theta1_min)/(theta2_max-theta2_min))
pl.axes().set_xlabel(r'$\theta_1$')
pl.axes().set_ylabel(r'$\theta_2$')
pl.show()

# <markdowncell>

# It is trivial to convert these parameters to LD50 to get Figure 3.4.

# <codecell>

pl.hist(-theta1s/theta2s, bins=20)
pl.axes().set_xlabel('LD50')
pl.axes().get_yaxis().set_visible(False)

# <markdowncell>

# ## Asymptotic Approximation (BDA 4.1) ## 
# 
# Alternatively, we can find the mode of the distribution, and use normal approximation at the mode.  For small problems like this, we can even avoid computing the actual gradient/Hessian by using numerical methods.

# <codecell>

import scipy.optimize

# <codecell>

# since I am lazy, let's use gradient-free optimization although analytic formula is available
res = scipy.optimize.minimize(lambda x: -log_posterior(x[0],x[1],bioassay_df.animals, bioassay_df.deaths, bioassay_df.dose), 
                              (0,0))

# <codecell>

theta_mode = res.x

# <codecell>

from scipy import linalg
def log_asymp_posterior_helper(theta_1, theta_2):
    theta_vec = np.matrix([theta_1,theta_2])
    return -(theta_vec - theta_mode) * linalg.solve(res.hess_inv,(theta_vec - theta_mode).transpose())

log_asymp_posterior = \
    np.vectorize(log_asymp_posterior_helper, otypes=[np.float])

# <markdowncell>

# Now Figure 4.1 (a) can be reproduced:

# <codecell>

import pylab as pl
grid_num = 64
theta1_min = -4
theta1_max = 10
theta2_min = -10
theta2_max = 40
x = np.linspace(theta1_min, theta1_max, grid_num)
y = np.linspace(theta2_min, theta2_max, grid_num)
X, Y = np.meshgrid(x, y)
log_Z = log_asymp_posterior(X,Y)
max_log_Z = log_Z.max()
Z = np.exp(log_Z - max_log_Z) * np.exp(max_log_Z)
levels=np.exp(max_log_Z) * np.linspace(0.05, 0.95, 10)
pl.axes().set_aspect(float(theta1_max-theta1_min)/(theta2_max-theta2_min))
pl.contourf(X, Y, Z, 8, alpha=.75, cmap='jet', 
            levels=np.exp(max_log_Z) * np.concatenate(([0], np.linspace(0.05, 0.95, 10), [1])))
pl.contour(X, Y, Z, 8, colors='black', linewidth=.5, levels=levels)
pl.axes().set_xlabel(r'$\theta_1$')
pl.axes().set_ylabel(r'$\theta_2$')

# <codecell>


