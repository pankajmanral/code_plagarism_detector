public class FindIndex {
    public static int findVal(int[] nums, int goal) {
        int left = 0;
        int right = nums.length - 1;

        while (left <= right) {
            int middle = (left + right) >>> 1; // Slightly different but functionally similar
            if (nums[middle] == goal) {
                return middle;
            }
            if (nums[middle] < goal) {
                left = middle + 1;
            } else {
                right = middle - 1;
            }
        }
        return -1;
    }
}
