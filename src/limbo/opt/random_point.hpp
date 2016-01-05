#ifndef LIMBO_OPT_RANDOM_POINT_HPP
#define LIMBO_OPT_RANDOM_POINT_HPP

#include <Eigen/Core>
#include <limbo/tools/random_generator.hpp>

namespace limbo {
    namespace opt {
        template <typename Params>
        struct RandomPoint {
            template <typename F>
            Eigen::VectorXd operator()(const F& f, bool bounded) const
            {
                // Random point does not support unbounded search
                assert(bounded);
                return tools::random_vector(f.param_size());
            }
        };
    }
}

#endif
