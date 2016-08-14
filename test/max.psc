PROGRAM PrintBiggestNumber
BEGIN
    entered_number <- 0
    biggest_number <- 0
    FOR count = 1 TO 3
        INPUT entered_number
        IF entered_number > biggest_number THEN
            biggest_number = entered_number
        END IF
    NEXT
    OUTPUT biggest_number
END