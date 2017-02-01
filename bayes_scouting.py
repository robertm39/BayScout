# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 17:44:03 2017

@author: rober
"""

import pymc as pm
import pylab as pyl

success_rate = pm.Uniform('success_rate', lower=0, upper=1)

observed = []

for i in range(0, 10):
    one_obs = pm.Bernoulli("obs " + i.__str__(), success_rate, value=1, observed=True)
    observed.append(one_obs)

all_nodes = []
all_nodes.extend(observed)
all_nodes.append(success_rate)

model = pm.Model(all_nodes)
mcmc = pm.MCMC(model)
mcmc.sample(60000, 50000, 5)

success_rate_samples = mcmc.trace('success_rate')[:]
pyl.hist(success_rate_samples)
pyl.show()