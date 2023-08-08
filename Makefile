test:
	helm upgrade --install --debug -n customer-monitoring-system --set-file script_py=./tmp/script.py -f ./tmp/values.test.yaml s3-metrics ./helm

template:
	helm template --debug --output-dir=./tmp/ -n customer-monitoring-system --set-file script_py=./tmp/script.py -f ./tmp/values.test.yaml s3-metrics ./helm

