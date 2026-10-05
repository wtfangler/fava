package dev.fancyvanilla.journal;

/** Natural identifier order without parsing arbitrary digit runs into a fixed-size number. */
final class NaturalOrder {
    private NaturalOrder() { }

    static int compare(String a, String b) {
        int i = 0, j = 0;
        while (i < a.length() && j < b.length()) {
            char x = a.charAt(i), y = b.charAt(j);
            if (x >= '0' && x <= '9' && y >= '0' && y <= '9') {
                int ai = i, bj = j;
                while (i < a.length() && a.charAt(i) >= '0' && a.charAt(i) <= '9') i++;
                while (j < b.length() && b.charAt(j) >= '0' && b.charAt(j) <= '9') j++;
                while (ai < i - 1 && a.charAt(ai) == '0') ai++;
                while (bj < j - 1 && b.charAt(bj) == '0') bj++;
                int cmp = Integer.compare(i - ai, j - bj);
                if (cmp != 0) return cmp;
                while (ai < i) {
                    cmp = Character.compare(a.charAt(ai++), b.charAt(bj++));
                    if (cmp != 0) return cmp;
                }
            } else {
                if (x != y) return Character.compare(x, y);
                i++;
                j++;
            }
        }
        int cmp = Integer.compare(a.length() - i, b.length() - j);
        return cmp != 0 ? cmp : a.compareTo(b);
    }
}
