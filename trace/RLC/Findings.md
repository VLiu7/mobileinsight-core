1. 沙尘天ping有30.05%的下行packet因为在接收窗口之外被拒收， 晴天下ping为27.94%，晴天下浏览器为45.10%

2. ping下无论何种天气，都会每隔一段时间出现一个被reject的packet，而浏览器则无此种规律

3. 沙尘天下行序列号出现突变

4. 被拒收的主要原因是duplicate packet

   1. 统计百分比：重复的block；重传的block；第一次传输就失败的block

   |                  |                           | 沙尘，ping | 晴天，ping | 晴天，浏览器 |
   | ---------------- | ------------------------- | ---------- | ---------- | ------------ |
   | 重复             | 因为CRC error而导致的重复 | 2.30       | 0.13       | 0.00         |
   |                  | 因为其他原因而导致的重复  | 27.21      | 27.81      | 41.18        |
   | 重传             | 重传                      | 0.06       | 0          | 0            |
   |                  | 重传成功                  | 0          | 0          | 0            |
   |                  | 重传失败                  | 0.06       | 0          | 0            |
   | 第一次传输就失败 | /                         | 0.48       | 0          | 3.92         |
   | 被拒绝           | /                         | 30.05      | 27.94      | 45.10        |

   注：被拒绝 = 重复 + 重传失败 + 第一次传输就失败

   2. 结论：
      1. 只有沙尘天存在重传
      2. 无论何种天气，大部分被拒绝的block都是因为duplicate而非重传
      3. 所有的CRC error都发生在某个block第一次传输之后。这说明后续的duplicate block都是因为没有通过CRC check而导致的重传，并不是真正的重复。
      4. 某些block看似是重复（之前存在相同序列号且位于receiving window内的block），其实是重传。因为之前的block虽然序列号合法从而被接收，但是没有通过CRC check。**这说明RLC即使对于没有通过CRC check的block也会接收，并且将接收窗口向前滑动。**在沙尘天气下，这种因为CRC error而导致的重复比例高于晴天（2.30 vs 0.13）。这是因为沙尘天本身CRC error就较多。
      5. 经过统计，第一次传输就失败的block主要集中在开头，推测是开始收集之前的block的重传

5. 接收窗口（receiving window）的下边缘 = 已经收到的block的序列号最大值 + 1。不会管还没收到的、CRC error的block。