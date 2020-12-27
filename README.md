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

1 server & 1 client

packet lose rate:0.1

误码率:0.00005

| buffer\rate | 3000 | 10000 | 30000 | 50000 | 100000 |
| ----------- | ---- | ----- | ----- | ----- | ------ |
| **10**          | 85.8 | 81.4  | 76.2  | 56.1  | 33.0   |
| **50**          | 82.6 | 82.8  | 74.2  | 64.5  | 36.6   |
| **100**         | 83.0 | 81.8  | 74.8  | 68.2  | 40.5   |
