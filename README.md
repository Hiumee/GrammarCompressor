# Grammar Compressor

An attempt to make a lossless data compressor using a grammar-based approach. The compression and decompression are done assuming a fixed grammar

| File       | Original Size (bytes) | Compressed Size (bytes) | Compressed Size + Brotli (bytes) | Compression Ratio | Compression Ratio (+Brotli) | Only Brotli Compressed Size (bytes) | Only Brotli Compression Ratio | Only Brotli Advantage (bytes) |
|------------|----------------------|------------------------|------------------------------|------------------|----------------------|------------------------------|----------------------|--------------------|
| 1.json     | 582                  | 430                    | 374                          | 0.74             | 0.64                 | 233                          | 0.40                 | 197                |
| 2.json     | 261                  | 192                    | 193                          | 0.73             | 0.74                 | 127                          | 0.49                 | 65                 |
| 3.json     | 603                  | 442                    | 369                          | 0.73             | 0.61                 | 238                          | 0.39                 | 204                |
| 4.json     | 3467                 | 3024                   | 2015                         | 0.87             | 0.58                 | 920                          | 0.27                 | 2104               |
| 5.json     | 872                  | 625                    | 462                          | 0.72             | 0.53                 | 257                          | 0.29                 | 368                |
| 6.json     | 65                   | 47                     | 51                           | 0.72             | 0.78                 | 61                           | 0.94                 | -14                |
