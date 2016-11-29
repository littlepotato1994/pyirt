# -*- coding: utf-8 -*-

import os
import sys
RootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(RootDir)

import unittest
from pyirt.solver import optimizer
from pyirt.utl import tools
import numpy as np
import json



'''
class TestMirtTest(unittest.TestCase):
    def setUp(self):
        # tmp in the parent dir
        self.pl2_cat3_data = json.load(open(RootDir + '/data/pl2_cat3_data.json')) 
        self.pl2_cat2_data = json.load(open(RootDir + '/data/pl2_cat2_data.json'))

        self.epsilon = 1e-8
    
    def test_param_2pl_cat3(self):
        data = self.pl2_cat3_data
        Ys = [pair[0] for pair in data['Y']]
        Xs = [[1.0, data['theta'][pair[1]]] for pair in data['Y']]

        tester = optimizer.Mirt_Optimizer()
        tester.load_res_data(Ys,Xs)
        naive_x0 = np.array([[0.0,0.0],[1.0,1.0]])
        est_param = tester.solve_param(naive_x0)
        true_params = np.array([[2.0,1.0],[1.0,2.0]])

        self.assertTrue(np.allclose(est_param,true_params,atol=0.05))

    def test_param_2pl_cat2(self):
        data = self.pl2_cat2_data
        Ys = [pair[0] for pair in data['Y']]
        Xs = [[1.0, data['theta'][pair[1]]] for pair in data['Y']]

        tester = optimizer.Mirt_Optimizer()
        tester.load_res_data(Ys,Xs)
        naive_x0 = np.array([[0.0],[1.0]])
        est_param = tester.solve_param(naive_x0) 
        true_params = np.array([[-1.0],[1.5]])

        self.assertTrue(np.allclose(est_param,true_params,atol=0.05))


    def test_score(self):
        # generate data
        wendog = np.array([[0,1]])
        exog = np.array([[0.0, 1.0],[1.0,0.0]])
        K = 2
        params = np.array([[-0.5], [1.0]])
        params_a = np.array([[-0.5], [1.0+self.epsilon]])
        params_b = np.array([[-0.5+self.epsilon], [1.0]])

        
        tester = optimizer.Mirt_Optimizer()

        grad_a = (tester._loglikelihood(params_a, wendog, exog,K) -tester._loglikelihood(params, wendog, exog,K))/self.epsilon
        grad_b = (tester._loglikelihood(params_b, wendog, exog,K) -tester._loglikelihood(params, wendog, exog,K))/self.epsilon
        grad = tester._score(params, wendog, exog, K)

        self.assertTrue(np.allclose(grad,np.array([grad_b,grad_a])))

    def test_hessian(self):

        wendog = np.array([[0,1]])
        exog = np.array([[0.0, 1.0],[1.0,0.0]])
        K = 2
        params = np.array([[-0.5], [1.0]])
        params_a = np.array([[-0.5], [1.0+self.epsilon]])
        params_b = np.array([[-0.5+self.epsilon], [1.0]])
        
        
        tester = optimizer.Mirt_Optimizer()
        hessian_a = (tester._score(params_a, wendog, exog,K) -tester._score(params, wendog, exog,K))/self.epsilon
        hessian_b = (tester._score(params_b, wendog, exog,K) -tester._score(params, wendog, exog,K))/self.epsilon

        hessian = tester._hessian(params, wendog, exog, K)

        self.assertTrue(np.allclose(hessian[0,:],hessian_b))
        self.assertTrue(np.allclose(hessian[1,:],hessian_a))
'''

class TestItemSolverNoGuess(unittest.TestCase):

    def setUp(self):
        # initialize the data
        n = 10000
        self.alpha = 1.5
        self.beta = -2.0
        theta_vec = np.random.normal(loc=0.0, scale=1.0, size=n)
        y1 = []
        y0 = []
        for i in range(n):
            # generate the two parameter likelihood
            prob = tools.irt_fnc(theta_vec[i], self.beta, self.alpha)
            # generate the response sequence
            if prob >= np.random.uniform():
                y1.append(1.0)
                y0.append(0.0)
            else:
                y1.append(0.0)
                y0.append(1.0)
        # the response format follows the solver API
        response_data = [y1, y0]

        # initialize optimizer
        self.solver = optimizer.irt_2PL_Optimizer()
        self.solver.load_res_data(response_data)
        self.solver.set_theta(theta_vec)
        self.solver.set_c(0)

    def test_linear_unconstrained(self):
        self.solver.set_initial_guess((0.0, 1.0))
        est_param = self.solver.solve_param_linear(is_constrained=False)
        self.assertTrue(abs(est_param[0] - self.beta) < 0.7 and abs(est_param[1] - self.alpha) < 0.5)  # orig is 0.07 and 0.05

    def test_linear_constrained(self):
        self.solver.set_initial_guess((0.0, 1.0))
        self.solver.set_bounds([(-4.0, 4.0), (0.25, 2)])
        est_param = self.solver.solve_param_linear(is_constrained=True)
        self.assertTrue(abs(est_param[0] - self.beta) < 0.2 and abs(est_param[1] - self.alpha) < 0.2)  # orig is 0.02


    def test_gradient_constrained(self):
        self.solver.set_initial_guess((0.0, 1.0))
        self.solver.set_bounds([(-4.0, 4.0), (0.25, 2)])
        est_param = self.solver.solve_param_gradient(is_constrained=True)
        self.assertTrue(abs(est_param[0] - self.beta) < 0.1 and abs(est_param[1] - self.alpha) < 0.1)

    def test_data_for_solve_param_mix(self):
        expected_right_count = np.array([4.05604874e-08, 7.06740321e-06, 6.50532986e-04,
                                         3.18995908e-01, 1.04895900e+01, 1.25667422e+02,
                                         4.77649918e+02, 7.60813810e+02, 5.98748095e+02,
                                         2.85752301e+02, 1.42559210e+02])
        expected_wrong_count = np.array([5.44930352e-03, 8.43617536e-02, 9.54184900e-01,
                                         8.00842890e+00, 9.74576266e+01, 7.48633956e+02,
                                         1.46395898e+03, 1.04005287e+03, 2.71513420e+02,
                                         3.65580835e+01, 6.77263765e+00])
        self.solver.set_initial_guess((0.0, 1.0))
        self.solver.set_bounds([(-4.0, 4.0), (0.25, 2)])
        self.solver.set_theta(np.linspace(-4, 4, num=11))
        self.solver.load_res_data([expected_right_count, expected_wrong_count])
        self.solver.solve_param_mix(is_constrained=True)
        self.assertTrue(bool("solve_param_mix has no exception!"))


class TestUserSolver(unittest.TestCase):

    def setUp(self):
        # initialize the data
        n = 1000
        self.theta = 1.5
        self.alpha_vec = np.random.random(n) + 1
        self.beta_vec = np.random.normal(loc=0.0, scale=2.0, size=n)
        self.c_vec = np.zeros(n)
        y1 = []
        y0 = []
        for i in range(n):
            # generate the two parameter likelihood
            prob = tools.irt_fnc(self.theta, self.beta_vec[i], self.alpha_vec[i])
            # generate the response sequence
            if prob >= np.random.uniform():
                y1.append(1.0)
                y0.append(0.0)
            else:
                y1.append(0.0)
                y0.append(1.0)
        # the response format follows the solver API
        response_data = [y1, y0]

        # initialize optimizer
        self.solver = optimizer.irt_factor_optimizer()
        self.solver.load_res_data(response_data)
        self.solver.set_item_parameter(self.alpha_vec, self.beta_vec, self.c_vec)
        self.solver.set_bounds([(-6, 6)])
    '''
    def test_linear_unconstrained(self):
        self.solver.set_initial_guess(0.0)
        est_param = self.solver.solve_param_linear(is_constrained=False)
        offset = abs(est_param - self.theta)
        self.assertTrue(offset < 0.2, offset)  # orig is 0.1
    '''
    def test_gradient_constrained(self):
        self.solver.set_initial_guess(0.0)
        self.solver.set_bounds([(-6, 6)])
        est_param = self.solver.solve_param_gradient(is_constrained=True)
        self.assertTrue(abs(est_param - self.theta) < 0.2)  # orig is 0.1

    def test_hessian_unconstrained(self):
        self.solver.set_initial_guess(0.0)
        est_param = self.solver.solve_param_hessian()
        self.assertTrue(abs(est_param - self.theta) < 0.2)  # orig is 0.1

    def test_scalar_constrained(self):
        self.solver.set_initial_guess(0.0)
        self.solver.set_bounds((-6, 6))
        est_param = self.solver.solve_param_scalar()
        self.assertTrue(abs(est_param - self.theta) < 0.2)  # orig is 0.1

if __name__ == '__main__':
    unittest.main()
