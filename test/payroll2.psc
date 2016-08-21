MODULE GetDay
PARAM day_index
BEGIN
    IF day_index=1
        RETURN 'Monday'
    ELSE IF day_index=2
        RETURN 'Tuesday'
    ELSE IF day_index=3
        RETURN 'Wednesday'
    ELSE IF day_index=4
        RETURN 'Thursday'
    ELSE IF day_index=5
        RETURN 'Friday'
    ELSE IF day_index=6
        RETURN 'Saturday'
    ELSE IF day_index=7
        RETURN 'Sunday'
    ELSE
        RETURN ''
    END IF
END

MODULE GetPositiveNumber
PARAM prompt
BEGIN
    in = -1
    WHILE in < 0
        OUTPUT prompt
        INPUT NUMBER in
        IF in < 0
            OUTPUT "Please enter a positive number or 0."
        END IF
    REPEAT

    RETURN in
END

PROGRAM PayrollCalculator
BEGIN
    normal_rate = GetPositiveNumber("Enter $/hour for normal pay: ")
    wkend_rate = GetPositiveNumber("Enter $/hour for weekend pay: ")
    overtime_rate = GetPositiveNumber("Enter $/hour for overtime pay: ")
    overtime_threshold = GetPositiveNumber("Enter the usual number of hours per day:")

    total_pay = 0.0
    FOR i=1 TO 7 DO
        hours_worked = GetPositiveNumber("Enter hours worked for " + GetDay(i))

        IF i > 5
            total_pay = total_pay + (wkend_rate * hours_worked)
        ELSE
            total_pay = total_pay + (normal_rate * hours_worked)
        END IF

        overtime_hours <- hours_worked - overtime_threshold
        IF overtime_hours > 0
            total_pay = total_pay + (overtime_rate * overtime_hours)
        END IF
    NEXT

    OUTPUT "Total pay: $", total_pay
END