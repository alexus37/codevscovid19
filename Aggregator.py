import numpy as np
from sklearn.neighbors import KernelDensity, BallTree, KDTree
import math

def sort_array_by_column(X, col_index):
    X = X[X[:, col_index].argsort(X)]
    return X

class Aggregator(object):

    def __init__(self):
        pass

    def update(self, X : np.ndarray):
        raise NotImplementedError()

    def sample_heatmap(self, num_samples):
        raise NotImplementedError()

    def get_infection_likelihood(self, X_track):
        raise NotImplementedError()


class TimeDiscretizedAggregator(Aggregator):

    def __init__(self, time_interval=3600):
        super().__init__()
        self.X = {} # time : nsamples x 3 array
        self.aggregators = {}
        self.time_interval = time_interval

    def _initialize_tree(self):
        for key in self.X.keys():
            self.aggregators[key] = KDTree(self.X[key])

    def update(self, X_new):
        X_new = np.copy(X_new)
        # X_new = X_new[X_new[:, 2].argsort(X_new)]
        X_new = sort_array_by_column(X_new, 2)
        for i in range(X_new.shape[0]):
            time = X_new[i, 2]
            frac = time/self.time_interval

            discretized_time = frac - math.floor(frac)
            if discretized_time < 0.5:
                key = math.floor(frac) * self.time_interval
            else:
                key = math.ceil(frac) * self.time_interval

            if key not in self.X:
                self.X[key] = []
            else:
                self.X[key] += [X_new[i, :]]
        self._initialize_tree()


class TimeSmoothAggregatorBase(Aggregator):

    def __init__(self, dimension_scales = None, disregard_time=False):
        super().__init__()
        self.disregard_time = disregard_time
        self.X = None # time : nsamples x 3 array
        self.aggregator = None
        self.dimension_scales = dimension_scales or np.ones(3)

    def _scale_input(self, X):
        return X*self.dimension_scales

    def _unscale_input(self, X):
        return X/self.dimension_scales

    def update(self, X_new):
        X_new = self._unscale_input(X_new)
        if self.disregard_time:
            X_new = X_new[:,:2]
        if self.X is None:
            self.X = X_new
        else:
            self.X = np.concatenate((self.X, X_new), axis=0)
        self._initialize()

    def _initialize(self):
        raise NotImplementedError()


class TimeSmoothAggregatorKDTree(TimeSmoothAggregatorBase):

    def _initialize(self):
        self.aggregator = KDTree(self.X)

    def get_infection_likelihood(self, X_track):
        # self.aggregator = KDTree()
        bandwidth = 10.0
        likelihoods = self.aggregator.kernel_density(X_track, bandwidth)
        return np.prod(likelihoods)

    def sample_heatmap(self, num_samples):
        # 1) sample points inside the tree somehow (uniformly?)

        # 2) call kernel density on each one to obtain their corresponding scores

        # 3) return the sampled points and their scores
        raise NotImplementedError()
        # return None


class TimeSmoothAggregatorKernelDensity(TimeSmoothAggregatorBase):

    def __init__(self, bandwidth = None, kernel = None, disregard_time=False):
        super().__init__(disregard_time=disregard_time)
        self.bandwidth = bandwidth or 1.0
        self.kernel = kernel or 'gaussian'

    def _initialize(self):
        self.aggregator = KernelDensity(bandwidth=self.bandwidth, kernel=self.kernel)
        self.aggregator.fit(self.X)

    def get_infection_likelihood(self, X_track):
        X_track = self._unscale_input(X_track)
        if self.disregard_time:
            X_track = X_track[:, :2]
        # self.aggregator = KernelDensity()
        # likelihoods = np.exp(self.aggregator.score_samples(X_track))
        likelihoods = self.aggregator.score_samples(X_track)

        total_score = np.sum(likelihoods)
        order = np.argsort(likelihoods)[::-1]
        return total_score, likelihoods, order

    def sample_heatmap(self, num_samples):
        # self.aggregator = KernelDensity()
        rand_state = np.random.RandomState(0)
        heatmap_samples = self.aggregator.sample(num_samples, rand_state)
        sample_scores = self.aggregator.score_samples(heatmap_samples)
        # sample_scores = np.exp(self.aggregator.score_samples(heatmap_samples))
        if self.disregard_time:
            heatmap_samples = np.concatenate([heatmap_samples, np.ones(shape=(heatmap_samples.shape[0],1 ), dtype=heatmap_samples.dtype)], axis=1)
        heatmap_samples = self._scale_input(heatmap_samples)
        return heatmap_samples, sample_scores

    def plot(self, grid_resolution=1000):
        from matplotlib import pyplot as plt
        x_min = self.X[:, 0].min()
        x_max = self.X[:, 0].max()
        y_min = self.X[:, 1].min()
        y_max = self.X[:, 1].max()
        # z_min = self.X[2].min()
        # z_max = self.X[2].max()
        if not self.disregard_time:
            z_min = 0
            z_max = 1

        grid_size = (x_max - x_min)/grid_resolution

        x_grid = np.arange(x_min, x_max, grid_size)
        y_grid = np.arange(y_min, y_max, grid_size)

        print("Resolution of the plot grid is: ")
        print(x_grid.size)
        print(y_grid.size)

        if not self.disregard_time:
            z_grid = np.arange(z_min, z_max, grid_size)
            X, Y, Z = np.meshgrid(x_grid, y_grid, z_grid)
            xyz = np.vstack([Y.ravel(), X.ravel(), Z.ravel()]).T
        else:
            X, Y = np.meshgrid(x_grid, y_grid)
            xyz = np.vstack([Y.ravel(), X.ravel()]).T

        print("Computing the heatmap values for the grid")
        # heat_values = np.exp(self.aggregator.score_samples(xyz))
        heat_values = self.aggregator.score_samples(xyz)

        print("Values computed")

        # plot contours of the density
        # levels = np.linspace(0, Z.max(), 25)
        # plt.contourf(X, Y, Z, levels=levels, cmap=plt.cm.Reds)
        # if not self.disregard_time:
        heatmap = heat_values.reshape(Y.shape[:2])
        # else:
        #     heatmap = heat_values

        plt.figure()
        plt.imshow(heatmap, cmap='jet')
        plt.colorbar()
        plt.figure()
        plt.plot(self.X[:, 0], self.X[:, 1], '.')

        plt.figure()
        # print("Sampling heatmap")
        # points, scores = self.sample_heatmap(1000)
        # print("Done")
        # plt.plot(points[:, 0], points[:, 1], '.')
        plt.show()


def create_test_samples(num_clusters=10):
    X = []
    for i in range(num_clusters):
        x_center = (np.random.rand(1)*1000)[0]
        y_center = (np.random.rand(1)*1000)[0]
        z_center = 1

        x_sig = np.random.rand(1)*200 + 50
        y_sig = np.random.rand(1)*200 + 50
        z_sig = 1


        X += [np.random.multivariate_normal(mean=np.array([x_center, y_center, z_center]),
                                           cov=np.array([[x_sig, 0, 0],
                                                         [0, y_sig, 0],
                                                         [0, 0, z_sig]]),
                                           size=8000
                                           )]
    X_uniform = np.random.rand(2000, 3)
    X_uniform[:, 0] *= 1000
    X_uniform[:, 1] *= 1000
    # # X[:, 2] *= 3600*10
    X_uniform[:, 2] *= 0.

    X += [X_uniform]

    X = np.concatenate(X, axis=0)
    return X



if __name__ == "__main__":
    # X = np.random.rand(10000, 3)
    # # X[:, 0] *= 1000
    # # X[:, 1] *= 2000
    # # X[:, 2] *= 3600*10
    # X[:, 2] *= 0.

    # X1 = np.random.multivariate_normal(mean=np.array([800, 800, 0]),
    #                               cov=np.array([[140, 0, 0],
    #                                             [0, 200, 5],
    #                                             [0, 0, 1]]),
    #                               size=8000
    #                               )
    # X2 = np.random.multivariate_normal(mean=np.array([100, 200, 0]),
    #                               cov=np.array([[200, 0, 0],
    #                                             [0, 150, 5],
    #                                             [0, 0, 1]]),
    #                               size=2000
    #                               )
    # X3 = np.random.rand(2000, 3)
    # X3[:, 0] *= 1000
    # X3[:, 1] *= 1000
    # # # X[:, 2] *= 3600*10
    # X3[:, 2] *= 0.
    #
    # X = np.concatenate([X1, X2, X3], axis=0)

    X = create_test_samples()
    X[:, 2] *= 0.

    # aggregator = TimeDiscretizedAggregator()
    # bandwidth = 1.
    # bandwidth = 10.
    bandwidth = 50.
    aggregator = TimeSmoothAggregatorKernelDensity(bandwidth=bandwidth)
    aggregator.update(X)
    total_score, likelihoods, sorted_indices = aggregator.get_infection_likelihood(X[:50])
    heatmap_samples, heatmap_scores = aggregator.sample_heatmap(num_samples=1000)
    aggregator.plot()

    print("Done")


