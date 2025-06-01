; SCIoT_G02_2025 domain

(define (domain SCIoT_G02_2025)

(:requirements :strips :typing :negative-preconditions)

(:types floor room sensor actuator - object
    binary_s numerical_s textual_s - sensor
    button_s motion_s - binary_s
    temperature_s humidity_s light_s sound_s rotation_s - numerical_s
    ; - textual_s
    binary_a numerical_a textual_a - actuator
    switch_a light_switch_a - binary_a
    light_dimmer_a - numerical_a
    display_a - textual_a
)

(:predicates
    (is_part_of ?room - room ?floor - floor) ; is the room part of this floor
    ;(is_part_of ?sensor - sensor ?room - room) ; is the sensor part of this room
    ;(is_part_of ?actuator - actuator ?room - room) ; is the actuator part of this room
    (is_next_to ?room1 - room ?room2 - room) ; are the rooms next to each other
    (is_ocupied ?room - room) ; is the room ocupied
    (is_cleaned ?room - room) ; is the room cleaned
    (is_sensing ?sensor - binary_s) ; is the sensor prodicing a signal
    ;(is_pressed ?button - button_s) ; is the button pressed
    ;(detects_motion ?motion - motion_s) ; is a motion detected
    (is_activated ?actuator - actuator) ; is a actuator on
    ;(is_on ?light - light_a) ; is a lightsource on
)

; this action turns on the light
(:action turn_on
    :parameters (?actuator - binary_a)
    :precondition (and
        ; we only ever need to do it once
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_activated ?actuator)
    )
)
(:action turn_off
    :parameters (?actuator - binary_a)
    :precondition (and
        ; we only ever need to do it once
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))
    )
)
(:action increase_a
    :parameters (?actuator - numerical_a)
    :precondition (and
        ; we only ever need to do it once
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_activated ?actuator)
    )
)
(:action decrease_a
    :parameters (?actuator - numerical_a)
    :precondition (and
        ; we only ever need to do it once
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))
    )
)

)