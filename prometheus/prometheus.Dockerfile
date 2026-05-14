FROM prom/prometheus
WORKDIR /etc/prometheus

COPY prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090
