// You have N gardens, labelled 1 to N.  In each garden, you want to plant one of 4 types of flowers.
//
// paths[i] = [x, y] describes the existence of a bidirectional path from garden x to garden y.
//
// Also, there is no garden that has more than 3 paths coming into or leaving it.
//
// Your task is to choose a flower type for each garden such that, for any two gardens connected by a path, they have different types of flowers.
//
// Return any such a choice as an array answer, where answer[i] is the type of flower planted in the (i+1)-th garden.  The flower types are denoted 1, 2, 3, or 4.  It is guaranteed an answer exists.
//
//  
//
//
// Example 1:
//
//
// Input: N = 3, paths = [[1,2],[2,3],[3,1]]
// Output: [1,2,3]
//
//
//
// Example 2:
//
//
// Input: N = 4, paths = [[1,2],[3,4]]
// Output: [1,2,1,2]
//
//
//
// Example 3:
//
//
// Input: N = 4, paths = [[1,2],[2,3],[3,4],[4,1],[1,3],[2,4]]
// Output: [1,2,3,4]
//
//
//  
//
// Note:
//
//
// 	1 <= N <= 10000
// 	0 <= paths.size <= 20000
// 	No garden has 4 or more paths coming into or leaving it.
// 	It is guaranteed an answer exists.
//
//
//
//


class Solution {
public:
    vector<int> gardenNoAdj(int N, vector<vector<int>>& paths) {
        vector<int> ans(N, -1);
        vector<vector<int>> graph(N + 1);
        for (vector<int> x : paths) {
            graph[x[0]].emplace_back(x[1]);
            graph[x[1]].emplace_back(x[0]);
        }
        for (int i = 1; i <= N; i++) {
            if (ans[i - 1] == -1) {
                set<int> temp;
                for (int x : graph[i]) {
                    temp.insert(ans[x - 1]);
                }
                for (int j = 1; j <= 4; j++) {
                    if (temp.find(j) == temp.end()) {
                        ans[i - 1] = j;
                        break;
                    }
                }
            }
        }
        return ans;
    }
};
