# Diamond pattern of stars
n = 5  # Number of rows for the upper half of the diamond

# Upper half of the diamond
for i in range(n):
    print(" " * (n - i - 1) + "*" * (2 * i + 1))

# Lower half of the diamond
for i in range(n - 2, -1, -1):
    print(" " * (n - i - 1) + "*" * (2 * i + 1))
