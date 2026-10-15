import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.TreeSet;

public class Main {
    public static void main(String[] args) throws Exception {
        String line = new BufferedReader(new InputStreamReader(System.in)).readLine();
        if (line == null) System.exit(2);
        TreeSet<Integer> values = new TreeSet<>();
        if (!line.trim().isEmpty()) {
            try {
                for (String part : line.split(",", -1)) values.add(Integer.parseInt(part.trim()));
            } catch (NumberFormatException error) { System.exit(2); }
        }
        System.out.println(values.toString().replace(" ", ""));
    }
}
