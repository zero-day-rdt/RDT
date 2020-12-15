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

