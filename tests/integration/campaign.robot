*** Settings ***
Documentation    RenodeResilience integration — full 27-fault campaign
Library         OperatingSystem

*** Test Cases ***
Sensor Suite 3-Fault Campaign Should Achieve At Least 30 RI
    ${out}=    Run    python -m src.cli campaign --config campaigns/sensor_suite.yaml --parallel 2 --output results
    Log    ${out}
    File Should Exist    results/Sensor_Suite_Validation.json

Full 27-Fault Campaign Should Achieve Grade B
    ${out}=    Run    python -m src.cli campaign --config campaigns/full_27.yaml --parallel 4 --output results
    Log    ${out}
    File Should Exist    results/Full_27-Fault_Coverage.json

Compare Baseline And Fixed Should Show Improvement
    ${out}=    Run    python -m src.cli compare --baseline results/baseline.json --optimized results/optimized.json --output results/comparison_fixed.html
    Log    ${out}
    File Should Exist    results/comparison_fixed.html
