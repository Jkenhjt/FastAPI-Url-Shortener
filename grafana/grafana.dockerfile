FROM grafana/grafana
WORKDIR /etc/grafana

COPY datasource.yml /etc/grafana/provisioning/datasources/datasource.yml
COPY dashboards.yml /etc/grafana/provisioning/dashboards/dashboards.yml

COPY dashboard.json /etc/grafana/provisioning/dashboards/dashboard.json

EXPOSE 3000
