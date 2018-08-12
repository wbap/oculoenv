# oculoenv
Oculomotor task environments.

Task contents are mostly compatible with [Psychlab](https://arxiv.org/abs/1801.08116).

## Tasks

### Point to taget

![point to target task](./docs/images/point_to_target_task.png)

### Change detection

![change detection task](./docs/images/change_detection_task.png)

### Visual search

![visual search task](./docs/images/visual_search_task.png)

### Odd one out

![odd one out task](./docs/images/odd_one_out_task.png)

### Multiple object tracking

![multiple object traking task](./docs/images/multiple_object_tracking_task.png)

### Random dot motion discrimination

![random dot motion discrimination task](./docs/images/random_dot_task.png)


# Example

```python
import numpy as np
from oculoenv import PointToTargetContent, Environment

content = PointToTargetContent(target_size="small",
                               use_lure=True,
                               lure_size="large")
env = Environment(content)

for i in range(100):
    dx = np.random.uniform(low=-0.02, high=0.02)
    dy = np.random.uniform(low=-0.02, high=0.02)
    action = np.array([dx, dy])
    obs, reward, done, _ = env.step(action)

    if done:
        print("Episode terminated")
        obs = env.reset()
```

# Acknowledements

Some of the Opengl related code fragments are from [gym-duckietown](https://github.com/duckietown/gym-duckietown/).

