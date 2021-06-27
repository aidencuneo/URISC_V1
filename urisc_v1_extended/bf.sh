# Functions
is_line_ending => b1,b2,b3,b4,b5,b6,b7,b8 ((:! b1) & (:! b2) & (:! b3) & (:! b4) & b5 & (:! b6) & b7 & (:! b8))
eq => x,y (:! (x ^ y))
byte_eq => a1,a2,a3,a4,a5,a6,a7,a8,b1,b2,b3,b4,b5,b6,b7,b8 (!(eq a1 b1) & !(eq a2 b2) & !(eq a3 b3) & !(eq a4 b4) & !(eq a5 b5) & !(eq a6 b6) & !(eq a7 b7) & !(eq a8 b8))

# Trust me, this is necessary
0 = 0
1 = 1

# Code
label start

# Get input
b1 = in
b2 = in
b3 = in
b4 = in
b5 = in
b6 = in
b7 = in
b8 = in

# Check for '+' character
is_plus = !(byte_eq b1 b2 b3 b4 b5 b6 b7 b8 0 0 1 0 1 0 1 1)

# Check for '-' character

# Check if this is the last character
line_ending = !(is_line_ending b1 b2 b3 b4 b5 b6 b7 b8)

print b1 b2 b3 b4 b5 b6 b7 b8

ifn line_ending start
