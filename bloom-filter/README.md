# bloom-filter

My take on a Bloom filter. It answers one question: "did I see this before?"

The idea is that we don't store items at all. For each item we take k positions from hashes and set those bits to 1. To check, we look at the same bits. If at least one is 0 - the item is definitely not here. If all are 1 - probably here, but maybe other items just set these bits by accident.

So false positives are possible, false negatives are not. And we save a lot of memory: 1000 items with 1% error take around 1.2 KB, instead of keeping 1000 real strings.

Useful when "no" is cheap and "maybe" you can double check anyway. Like skipping a disk read, or filtering urls you already crawled.

## Usage

```python
from prototype import BloomFilter

bf = BloomFilter.from_capacity(1000, 0.01)  # 1000 items, 1% false positives
bf.add("hello")

bf.might_contain("hello")   # True
bf.might_contain("world")   # False (almost for sure)
```

`from_capacity` counts the params by the standard formulas, so you don't have to guess size and number of hashes. If you want, you can still do it by hand: `BloomFilter(size, num_hash)`.

Also added two small methods to look inside: `fill_ratio()` - how much of the array is already set, and `current_fp_rate()` - the error rate right now, not the theoretical one.

## Notes for myself

- I take only two hashes (md5 + sha1) and make k of them like `h1 + i*h2`. This is the Kirsch-Mitzenmacher trick, k real hashes are not needed.
- Size is rounded up to the next prime, so modulo spreads bits better.
- No delete here. If you clear the bits, you break other items that use the same bits. For delete you need a counting Bloom filter.
