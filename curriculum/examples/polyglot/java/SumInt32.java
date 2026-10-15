import java.util.Scanner;

public class SumInt32 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        if (!input.hasNext()) System.exit(2);
        String first = input.next();
        if (!input.hasNext()) System.exit(2);
        String second = input.next();
        if (input.hasNext()) System.exit(2);
        try {
            long a = Long.parseLong(first);
            long b = Long.parseLong(second);
            if (a < Integer.MIN_VALUE || a > Integer.MAX_VALUE || b < Integer.MIN_VALUE || b > Integer.MAX_VALUE) System.exit(2);
            long sum = a + b;
            if (sum < Integer.MIN_VALUE || sum > Integer.MAX_VALUE) System.exit(2);
            System.out.println(sum);
        } catch (NumberFormatException error) {
            System.exit(2);
        }
    }
}
