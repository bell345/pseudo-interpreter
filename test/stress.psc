MODULE addition
PARAM x
PARAM y
BEGIN
    z <- 23
    z = 24
    if z - 23 == 0 THEN
        output 'no second'
    ELSE IF z - 24 == 0 THEN
        OutPut 'second'
    else
        OUTPUT 'nzero'
    END IF

    OUTPUT('what\'s this?')
    OUTPUT(to_str(y)+'abc')

    y <- x + y

    RETURN y
END

PROGRAM StressTest
BEGIN
    x = 2
    y = 3
    x = addition(2, 3)
    OUTPUT x, y
END
