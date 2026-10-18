# Java Programming Core: Loops, Arrays, and Memory Layout

## Iteration and Loop Control
Java provides `for`, `enhanced-for` (for-each), `while`, and `do-while` loops for repeating algorithmic blocks.
Loop termination conditions must always be verifiable to avoid infinite execution cycles.
In array processing, index bounds must be strictly respected (`0 <= index < array.length`) to prevent `ArrayIndexOutOfBoundsException`.

## The Enhanced For Loop
For iterating through collections or arrays without index manipulation, the enhanced `for` loop provides clean, concise syntax:

```java
int[] numbers = {10, 20, 30, 40};
int sum = 0;
for (int num : numbers) {
    sum += num;
}
```

## Primitive Types vs Object Reference Variables
In Java, primitive types (`int`, `boolean`, `double`, `char`) store raw values directly on the call stack.
Object references (`String`, arrays, class instances) hold heap memory pointers. Equality comparison (`==`) between object references compares address identity, whereas the `.equals()` method compares substantive semantic value equality.
