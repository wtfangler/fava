package dev.fancyvanilla.journal;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** Run with plain javac/java; regression for server-provided identifiers overflowing long. */
public final class NaturalOrderTest {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        check(NaturalOrder.compare("quest/2a", "quest/10a") < 0, "Numeric quest order");
        check(NaturalOrder.compare("age/7", "age/12") < 0, "Numeric era order");
        check(NaturalOrder.compare("mod:quest/9223372036854775808", "mod:quest/9223372036854775809") < 0,
                "Runs exceeding Long.MAX_VALUE");
        check(NaturalOrder.compare("mod:quest/" + "9".repeat(4000), "mod:quest/1" + "0".repeat(4000)) < 0,
                "Unbounded digit runs");
        check(NaturalOrder.compare("quest/2a", "quest/002b") < 0, "Equal numeric runs continue with suffix");
        check(NaturalOrder.compare("quest/2a", "quest/002a") != 0, "Distinct leading-zero IDs have a total order");

        Random random = new Random(26_204);
        List<String> ids = new ArrayList<>(List.of("", "a", "a0", "a00", "a1", "a01", "a10", "a2", "a2b", "a02a"));
        for (int i = 0; i < 200; i++) {
            StringBuilder id = new StringBuilder("test:");
            for (int j = 0, count = random.nextInt(50) + 1; j < count; j++) {
                id.append("0123456789abc/_".charAt(random.nextInt(14)));
            }
            ids.add(id.toString());
        }
        for (String a : ids) {
            check(NaturalOrder.compare(a, a) == 0, "Reflexivity: " + a);
            for (String b : ids) {
                check(Integer.signum(NaturalOrder.compare(a, b)) == -Integer.signum(NaturalOrder.compare(b, a)),
                        "Antisymmetry: " + a + ", " + b);
            }
        }
        for (int i = 0; i < 40_000; i++) {
            String a = ids.get(random.nextInt(ids.size())), b = ids.get(random.nextInt(ids.size())), c = ids.get(random.nextInt(ids.size()));
            if (NaturalOrder.compare(a, b) <= 0 && NaturalOrder.compare(b, c) <= 0) {
                check(NaturalOrder.compare(a, c) <= 0, "Transitivity: " + a + ", " + b + ", " + c);
            }
        }
        ids.sort(NaturalOrder::compare);
        for (int i = 1; i < ids.size(); i++) {
            check(NaturalOrder.compare(ids.get(i - 1), ids.get(i)) <= 0, "TimSort order");
        }
        System.out.println("NaturalOrder: numeric overflow, leading zeros, 44,100 pair comparisons and 40,000 transitivity samples passed");
    }
}
