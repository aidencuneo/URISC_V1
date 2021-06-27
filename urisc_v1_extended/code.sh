xor_old => a,b ((a | b) & (:! (a & b)))
xor => a,b (a ^ b)

andor_result1 = ((a & b) | c)
andor_result2 = !(xor a b)

a = 0
b = 0

zero_zero = !(xor a b)

a = 0
b = 1

zero_one = !(xor a b)

a = 1
b = 0

one_zero = !(xor a b)

a = 1
b = 1

one_one = !(xor a b)
