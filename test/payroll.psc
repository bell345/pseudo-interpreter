PROGRAM Payroll_calculator
BEGIN
    Pay_hourlyrate <- 0.0
    Pay_overtimerate <- 0.0
    Hoursworked <- 0.0
    HoursOvertimeWorked <- 0.0
    Total <- 0.0
    INPUT Pay_hourlyrate
    IF Pay_hourlyrate = 0
        OUTPUT "Error message"
    ELSE
        INPUT Pay_overtimerate
        If Pay_overtimerate = 0
            OUTPUT "Error message"
        ELSE
            INPUT Hoursworked
            If Hoursworked = 0
                OUTPUT "Error message"
            ELSE
                INPUT HoursOvertimeWorked
                IF HoursOvertimeWorked = 0
                    OUTPUT "Error message"
                ELSE
                    Total = (Hoursworked * Pay_hourlyrate) + (HoursOvertimeWorked * Pay_overtimerate)
                END IF
                
            END IF
            
        END IF
        
    END IF
    
    OUTPUT Total
END