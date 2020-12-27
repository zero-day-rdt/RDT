| NAME                       | VALUE     |
| -------------------------- | --------- |
| SYN                        | 1 bit     |
| ACK                        | 1 bit     |
| FIN                        | 1 bit     |
| RST                        | 1 bit     |
| SAK                        | 1 bit     |
| placeholder                | 3 bits    |
| SEQ / SEQ_SAK （when SAK） | 4 bytes   |
| SEQ_ACK                    | 4 bytes   |
| LEN                        | 2 bytes   |
| CHECKSUM                   | 2 bytes   |
| PAYLOAD                    | LEN bytes |

two connection:

|buffer\rate| 3000  | 10000 | 30000 | 50000 | 100000    |
| --------  | ----  | ----- | ----- | ----- | ----      |
|     10    | 82.36 | 83.34 | 77.09 | 65.60 | 58.46     |
| 50        | 81.61 | 84.07 | 73.75 | 65.21 | 56.28     |
| 100       | 82.75 | 0     | 0     | 0     | 0         |

