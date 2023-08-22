test:
	helm upgrade --install --debug -n customer-monitoring-system --set-file script_py=./examples/s3-metrics.py -f ./tmp/values.test.yaml s3-metrics ./helm

test_cleanup:
	helm uninstall -n customer-monitoring-system s3-metrics

template:
	helm template --debug --output-dir=./tmp/ -n customer-monitoring-system --set-file script_py=./examples/s3-metrics.py -f ./tmp/values.test.yaml s3-metrics ./helm

chart_release:
	git checkout gh-pages
	git merge main
	git commit -m "merged"
	git push
	helm package ./helm
	helm repo index .
	git add .
	git commit -m "update chart"
	git push origin gh-pages
	git checkout main

.PHONY: test template chart_release
