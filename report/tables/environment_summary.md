| category | item | value | source |
| --- | --- | --- | --- |
| campaign | summary_generated_at_utc | 2026-05-22T01:16:15.513542+00:00 | script timestamp |
| host | os | Windows-11-10.0.26200-SP0 | platform.platform |
| host | python_executable | C:\Users\lucap\Documents\VSC Repository\flight-delay-big-data-analysis\.venv\Scripts\python.exe | sys.executable |
| host | python_version | 3.12.2 | platform.python_version |
| host | cpu_model | AMD64 Family 26 Model 96 Stepping 0, AuthenticAMD | platform.processor |
| host | physical_cores | 8 | psutil |
| host | logical_cores | 16 | psutil |
| host | ram_bytes | 33598853120 | psutil |
| host | project_drive_total_bytes | 957397069824 | psutil.disk_usage |
| host | project_drive_free_bytes | 542476943360 | psutil.disk_usage |
| host | windows_cpu_model | AMD Ryzen AI 7 350 w/ Radeon 860M | Win32_Processor |
| host | windows_os_detail | Microsoft Windows 11 Home 10.0.26200 build 26200 64-bit | Win32_OperatingSystem |
| host | disk_type | WD PC SN5000S SDEPMSJ-1T00-1101; media=SSD; bus=NVMe; size=1024209543168 | Get-PhysicalDisk |
| runtime | java_version | openjdk version "17.0.19" 2026-04-21 | java -version |
| runtime | docker_version | Docker version 29.4.3, build 055a478 | docker --version |
| runtime | docker_compose_version | Docker Compose version v5.1.3 | docker compose version |
| runtime | docker_desktop_limits | CPUs=16; MemBytes=16391536640; Server=29.4.3; OS=Docker Desktop | docker info |
| runtime | hive_base_image | apache/hive:4.0.1 | Dockerfile.hive |
| runtime | mapreduce_base_image | apache/hive:4.0.1 | Dockerfile.mapreduce |
| runtime | pyspark_version | 4.1.1 | Python import |
| runtime | pandas_version | 3.0.3 | Python import |
| runtime | pyarrow_version | 24.0.0 | Python import |
| spark_config | local_config_path | config/local.yaml | config yaml |
| spark_config | local_spark_master | local[*] | config yaml |
| spark_config | local_shuffle_partitions | 8 | config yaml |
| spark_config | local_execution_setting | local | config yaml |
| spark_config | docker-simulation_config_path | config/docker_simulation.yaml | config yaml |
| spark_config | docker-simulation_spark_master | spark://spark-master:7077 | config yaml |
| spark_config | docker-simulation_shuffle_partitions | 16 | config yaml |
| spark_config | docker-simulation_execution_setting | docker-compose Spark standalone: 1 master + 2 workers; Hive single-node container | config yaml |
| spark_config | docker-simulation_spark_driver_service | spark-driver | config yaml |
| spark_config | docker-simulation_container_workspace | /workspace | config yaml |
| docker_topology | compose_services | hive-metastore, hive-postgres, hiveserver2, mapreduce-runner, spark-core, spark-driver, spark-master, spark-worker-1, spark-worker-2 | docker-compose.yml |
| docker_topology | spark-worker-1_command | spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077 --host spark-worker-1 --webui-port 8081 --cores 2 --memory 2g | docker-compose.yml |
| docker_topology | spark-worker-2_command | spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077 --host spark-worker-2 --webui-port 8081 --cores 2 --memory 2g | docker-compose.yml |
| docker_topology | worker_count_variation | not used in M2; Compose defines two named workers | M2 plan |
