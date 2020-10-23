# acc-airfoil
Airfoil-as-a-Service to perform airfoil computations on OpenStack.

## Deploy main node
```
python deploy/deploy-instance.py \
  --cloudinit deploy/broker-init.yaml \
  --security_group [SECURITY GROUP] \
    g2-airfoil-main
```

## Deploy workers
```
python deploy/deploy-instance.py \
  --cloudinit deploy/worker-init.yaml \
  --flavor ssc.medium \
  --num_instances 2 \
    g2-airfoil-worker
```
