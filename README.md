# Malware Network Traffic Classifier
A random forest trained to detect malicious network traffic from BRO Log files. Built using python v2.7, scipy, numpy, and pandas. Trained, validated, and tested using the CTU Botnet datasets.

## CTU Datasets TO-USE:
### Training
- [CTU BOTNET - Capture 1](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-1/)

    **Infected Machines:**

        Windows Name: Win8, IP: 10.0.2.22 (Label: Botnet-V1)
        Windows Name: Win12, IP: 10.0.2.112 (Label: Botnet-V2)

- [CTU BOTNET - Capture 2](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-2/)

    **Infected Machines:**

        Windows Name: Win2, IP: 10.0.2.16 (Label: Botnet-V1)

- [CTU BOTNET - Capture 3](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-3/)

    **Infected Machines:**

        Windows Name: Win15, IP: 10.0.2.29 (Label: Botnet-V1)

- [CTU BOTNET - Capture 4](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-4/)

    **Infected Machines:**

        Windows Name: Win2, IP: 10.0.2.16 (Label: Botnet-V1)  - 2013-08-20_capture-win2
        Windows Name: Win5, IP: 10.0.2.19 (Label: Botnet-V2)  - 2013-08-20_capture-win5

- [CTU BOTNET - Capture 5](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-5/)

    **Infected Machines:**

        Windows Name: Win12, IP: 10.0.2.26 (Label: Botnet-V1)
        Windows Name: Win13, IP: 10.0.2.27 (Label: Botnet-V2)
        Windows Name: Win14, IP: 10.0.2.28 (Label: Botnet-V3)

### Validation
- [CTU NORMAL - Capture 20](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Normal-20/)
- [CTU NORMAL - Capture 21](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Normal-21/)
- [CTU NORMAL - Capture 22](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Normal-22/)
- [CTU NORMAL - Capture 23](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Normal-23/)

### Test
- [CTU MIXED - Capture 1](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Mixed-Capture-1/)

    **Unlabeled Dataset**

