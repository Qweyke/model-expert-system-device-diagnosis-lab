; ========================================
; Expert System: Diagnosis of Telematics Terminal-device 
; Purpose: Determine device malfunction by LED color, power status and internal state
; ========================================

(deffunction start ()
    "Function: Power on the system"
    (reset)
    (run)
)

(deffunction ask-with-validation (?question-str $?allowed-answers)
    "Function: Ask question about single attribute"
    (while TRUE
        (printout t ?question-str " [" ?allowed-answers "]: " crlf)
        (bind ?user-input (lowcase (read)))
        (if (member$ ?user-input ?allowed-answers) then
            (return ?user-input)
        else 
            (printout t "Validate answer: Fail / Allowed answers are: " ?allowed-answers crlf)
        )
    )
)


(deftemplate device
    "Template: Terminal-device status"
    (slot power (default unknown))
    (slot led-color (default unknown))
    (slot internal-state (default unknown))
)

(deffacts initial-device
    "Initial facts: Default device fact"
    (device)
)

(defrule check-power-status
    "Rule: Check power status. Is initial"
    ?dev_addr <- (device (power unknown))
    =>
    (modify ?dev_addr 
        (power (ask-with-validation "What is the power status for this device?" "on" "off"))
    )
    (printout t "Change device state: Success" crlf)
)


