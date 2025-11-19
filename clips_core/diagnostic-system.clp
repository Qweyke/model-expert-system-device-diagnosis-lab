; ========================================
; Expert System: Diagnosis of Telematics Terminal-device 
; Purpose: Determine device malfunction by LED color, power status and internal state
; ========================================

(deftemplate device
    "Template: Terminal-device status"

    (slot power 
        (type SYMBOL)
        (allowed-symbols on off unknown)
        (default unknown))
    (slot led-color 
        (type SYMBOL)
        (allowed-symbols red green yellow blue none unknown)
        (default unknown))
    (slot internal-state 
        (type SYMBOL)
        (allowed-symbols errfile erraddress unknown)
        (default unknown))
)

(deffunction start ()
    "Function: Power on the system, create device fact"

    (reset)
    (assert (device))
    (run)
)

(deffunction ask-slot-value-with-validation (?template-based-fact ?slot)
    "Function: Ask question to fill out one slot of the template"

    (bind ?allowed-inputs (deftemplate-slot-allowed-values ?template-based-fact ?slot))
    (if (eq ?allowed-inputs FALSE)
    then
        (printout t "Get allowed inputs: Fail / Slot " ?slot " allowed-values is empty" crlf)
        (halt)
    )

    (while TRUE
        (printout t "What's the status of " ?slot " - " ?allowed-inputs crlf)
        (bind ?user-input (lowcase (read)))
        (if (member$ ?user-input ?allowed-inputs)
        then
            (return ?user-input)
        else 
            (printout t "Validate answer: Fail / Allowed answers are: " ?allowed-inputs crlf)
        )
    )
)

(defrule check-power
    ?device-id <- (device (power unknown))
    =>
    (bind ?user-input (ask-slot-value-with-validation device power))
    (modify ?device-id (power ?user-input))
)

(defrule check-led-color
    ?device-id <- (device (power on) (led-color unknown))
    =>
    (bind ?user-input (ask-slot-value-with-validation device led-color))
    (modify ?device-id (led-color ?user-input))
)

(defrule check-internal-state
    ?device-id <- (device (power on) (led-color yellow))
    =>
    (bind ?user-input (ask-slot-value-with-validation device internal-state))
    (modify ?device-id (internal-state ?user-input))
)

(defrule diagnose-no-power
    (device (power off))
    =>
    (printout t "Diagnosis: Connect the power supply to device" crlf)
    (halt)
)

(defrule diagnose-led-none
   (device (power on) (led-color none))
   =>
   (printout t "Diagnosis: Hardware fault detected - send the board for physical diagnostics" crlf)
   (halt)
)

(defrule diagnose-led-red
   (device (power on) (led-color red))
   =>
   (printout t "Diagnosis: CPU malfunction - send the board for CPU reballing" crlf)
   (halt)
)

(defrule diagnose-led-yellow-errfile
   (device (power on) (led-color yellow) (internal-state errfile))
   =>
   (printout t "Diagnosis: Flash error - reflash device with Stable.bin image" crlf)
   (halt)
)

(defrule diagnose-led-yellow-erraddr
   (device (power on) (led-color yellow) (internal-state erraddress))
   =>
   (printout t "Diagnosis: Bootloader address fault - reflash device with Recovery.bin image" crlf)
   (halt)
)

(defrule diagnose-led-green-ok
   (device (power on) (led-color green))
   =>
   (printout t "Diagnosis: Device fully operational - ready for casing" crlf)
   (halt)
)

(defrule diagnose-hw-fault
   (device (power on) (led-color none))
   =>
   (printout t "Diagnosis: Hardware fault - board must be sent for physical inspection" crlf)
   (halt)
)

(defrule diagnose-led-blue
   (device (power on) (led-color blue))
   =>
   (printout t "Diagnosis: Firmware update process detected" crlf)
   (halt)
)
