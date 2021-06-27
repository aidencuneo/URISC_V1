a7 ?;a7 ?
a6 ?
a5 ?;a5 ?
a4 ?;a4 ?
a3 ?
a2 ?;a2 ?
a1 ?
a0 ?

b7 ?;b7 ?
b6 ?;b6 ?
b5 ?;b5 ?
b4 ?
b3 ?
b2 ?
b1 ?;b1 ?
b0 ?;b0 ?

/ / Unsaid variables:
bit0done = 0
bit1done = 0
. . .
bit7done = 0


/ / Begin the program


start_of_full_adder(a,b,c_in)

/ / Set a to 0
set_a_0
a set_a_0

/ / Set b to 0
set_b_0
b set_b_0

/ / Figure out which bit should be added next
bit0done bit0done_end
print ?
print ?
out ?
print ?
out ?
print ?
print ?
print ?
print ?
print ?

/ / Copy a0 into a
a0 a_copy_end_1
a ?
a_copy_end_1
a0 ?

/ / Copy b0 into b
b0 b_copy_end_1
b ?
b_copy_end_1
b0 ?

bit0done_end
bit0done ?

/ / Start addition

a xor_end_1
xor_result_1 ?
xor_end_1
a ?

b xor_end_2
xor_result_1 ?
xor_end_2
b ?

xor_result_1 xor_end_3
sum ?
xor_end_3
xor_result_1 ?

c_in xor_end_4
sum ?
xor_end_4
c_in ?

a and_end_1
b and_end_2
and_result_1 ?
and_end_2
b ?
and_end_1
a ?

xor_result_1 and_end_3
c_in and_end_4
and_result_2 ?
and_end_4
c_in ?
and_end_3
xor_result_1 ?

and_result_1 ?
and_result_1 or_end_1
and_result_2 ?
and_result_2 or_end_2
c_out ?
or_end_2
or_end_1
c_out ?

/ / Set c_in to 0
c_in_set_0
c_in c_in_set_0

/ / Copy c_out into c_in
c_out c_out_copy_end_1
c_in ?
c_out_copy_end_1
c_out ?

/ / Start full adder again
? start_of_full_adder(a,b,c_in)
? start_of_full_adder(a,b,c_in)

