; SCIoT_G02_2025 domain

(define (domain SCIoT_G02_2025)

(:requirements :adl)
; :adl >>> :strips :typing :negative-preconditions :equality :disjunctive-preconditions

(:types floor room room_position iot cleaning_team - object
    
    sensor actuator - iot

    binary_s numerical_s textual_s - sensor
    button_s motion_s virtual_switch_s - binary_s
    temperature_s humidity_s light_s sound_s rotation_s virtual_dimmer_s - numerical_s
    ; - textual_s

    binary_a numerical_a textual_a - actuator
    switch_a light_switch_a virtual_switch_a - binary_a
    light_dimmer_a virtual_dimmer_a - numerical_a
    display_a - textual_a
)

(:predicates
    ; topology
    (room_is_part_of_floor ?room - room ?floor - floor) ; is the room part of this floor
    (sensor_is_part_of_room ?sensor - sensor ?room - room) ; is the sensor part of this room
    (actuator_is_part_of_room ?actuator - actuator ?room - room) ; is the actuator part of this room
    (actuator_increases_sensor ?actuator - actuator ?sensor - sensor) ; is the actuator influencing this sensor
    (actuator_decreases_sensor ?actuator - actuator ?sensor - sensor) ; is the actuator influencing this sensor
    (is_next_to ?room1 - room ?room2 - room) ; are the rooms next to each other
    (is_at ?cleaning_team - cleaning_team ?room - room) ;

    ; problem to lock down a sensor that is part of two room positions
    (positioned_at ?iot - iot ?room_position - room_position)

    ;; meta context
    (is_ocupied ?room - room) ; is the room ocupied
    (will_become_ocupied ?room - room) ; is the room ocupied in the near future
    (is_cleaned ?room - room) ; is the room cleaned

    ; activity
    (has_specified_activity_at ?room - room ?room_position - room_position)
    (is_doing_read_at ?person_in_room - room ?room_position - room_position) ; some people in this room are reading
    (is_doing_sleep_at ?person_in_room - room ?room_position - room_position) ; some people in this room are sleeping
    (is_doing_bath_at ?person_in_room - room ?room_position - room_position) ; some people in this room are in the bathroom

    ; sensors
    (is_sensing ?sensor - sensor) ; is the sensor prodicing a signal
    ;(is_verylow ?sensor - numerical_s) ; non binary sensor level
    (is_low ?sensor - numerical_s) ; non binary sensor level
    (is_ok ?sensor - numerical_s) ; non binary sensor level
    (is_high ?sensor - numerical_s) ; non binary sensor level
    ;(is_veryhigh ?sensor - numerical_s) ; non binary sensor level

    ; actuators
    (is_activated ?actuator - actuator) ; is a actuator activated

    ; force checks predicate
    (fulfilled_activity ?room - room ?room_position - room_position) ; a lock that prevents actuators to change the state further after an action detects that the curent state fulfilles the activity requests 
    ; we expect that this is the last thing a planer does normaly
)

; needs :derived-predicates
;(:derived (is_connected ?r1 ?r2)
;  (or (is_next_to ?r1 ?r2) (is_next_to ?r2 ?r1))
;)
;(:derived (can_clean_now ?room - room)
;  (and
;    (not (is_ocupied ?room))
;    (not (will_become_ocupied ?room))
;    (not (is_cleaned ?room))
;  )
;)

; cleaning
(:action move_to_floor
    :parameters (?cleaning_team - cleaning_team ?curent_room ?next_room - room ?curent_floor ?next_floor - floor)
    :precondition (and
        (is_at ?cleaning_team ?curent_room)
        (or
            (is_next_to ?curent_room ?next_room)
            (is_next_to ?next_room ?curent_room)
        )
        (room_is_part_of_floor ?curent_room ?curent_floor)
        (room_is_part_of_floor ?next_room ?next_floor)
        (not (= ?curent_floor ?next_floor))
    )
    :effect (and
        (not (is_at ?cleaning_team ?curent_room))
        (is_at ?cleaning_team ?next_room)
    )
)

(:action move_to_room
    :parameters (?cleaning_team - cleaning_team ?curent ?next - room ?floor - floor)
    :precondition (and
        (is_at ?cleaning_team ?curent)
        (or
            (is_next_to ?curent ?next)
            (is_next_to ?next ?curent)
        )
        (room_is_part_of_floor ?curent ?floor)
        (room_is_part_of_floor ?next ?floor)
    )
    :effect (and
        (not (is_at ?cleaning_team ?curent))
        (is_at ?cleaning_team ?next)
    )
)

;what if there are isolated 2 rooms toghether
(:action move_to_isolated_room
    :parameters (?cleaning_team - cleaning_team ?curent ?next - room ?floor - floor)
    :precondition (and
        (is_at ?cleaning_team ?curent)
        (room_is_part_of_floor ?curent ?floor)
        (room_is_part_of_floor ?next ?floor)
        (forall (?other - room)
            (and
                (not (is_next_to ?other ?next))
                (not (is_next_to ?next ?other))
            )
        )
    )
    :effect (and
        (not (is_at ?cleaning_team ?curent))
        (is_at ?cleaning_team ?next)
    )
)

; TODO turn on lights to clean
(:action team_clean
    :parameters (?cleaning_team - cleaning_team ?room - room)
    :precondition (and
        (is_at ?cleaning_team ?room)
        (not (is_cleaned ?room))
        (not (is_ocupied ?room))
        (not (will_become_ocupied ?room))
    )
    :effect (and
        (is_cleaned ?room)
    )
)

;; assign if missing in problem file

; floor
(:action assign_floor
    :parameters (?room - room ?floor1 - floor)
    :precondition (and
        (forall (?floor2 - floor)
            (not (room_is_part_of_floor ?room ?floor2))
        )
    )
    :effect (and
        (room_is_part_of_floor ?room ?floor1)
    )
)

; room_position
(:action assign_room_position
    :parameters (?iot - iot)
    :precondition (and
        (forall (?room_position - room_position)
            (not (positioned_at ?iot ?room_position))
        )
    )
    :effect (and
        (forall (?room_position - room_position)
            (positioned_at ?iot ?room_position)
        )
    )
)

; actuator control
(:action turn_on
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (not (is_sensing ?sensor))
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_sensing ?sensor)
        (is_activated ?actuator)
    )
)

(:action turn_off
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_sensing ?sensor)
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_sensing ?sensor))
        (not (is_activated ?actuator))
    )
)

(:action turn_on_inverted
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (not (is_sensing ?sensor))
        (is_activated ?actuator)
    )
    :effect (and
        (is_sensing ?sensor)
        (not (is_activated ?actuator))
    )
)

(:action turn_off_inverted
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_sensing ?sensor)
        (not (is_activated ?actuator))
    )
    :effect (and
        (not (is_sensing ?sensor))
        (is_activated ?actuator)
    )
)

(:action increase_s_by_a_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_low ?sensor)
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_activated ?actuator)
        (not (is_low ?sensor))
        (is_ok ?sensor)
    )
)

(:action increase_s_by_na_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_low ?sensor)
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))
        (not (is_low ?sensor))
        (is_ok ?sensor)
    )
)

; can only influence one sensor at a time
(:action decrease_s_by_a_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_high ?sensor)
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_activated ?actuator)
        (not (is_high ?sensor))
        (is_ok ?sensor)
    )
)

(:action decrease_s_by_na_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room ?room_position - room_position)
    :precondition (and
        (not (fulfilled_activity ?room ?room_position))
        (positioned_at ?sensor ?room_position)
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_high ?sensor)
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))
        (not (is_high ?sensor))
        (is_ok ?sensor)
    )
)

; activity based actuator control
(:action detect_activity
    :parameters (?room - room ?room_position - room_position)
    :precondition (or
        (is_doing_read_at ?room ?room_position)
        (is_doing_sleep_at ?room ?room_position)
        (is_doing_bath_at ?room ?room_position)
    )
    :effect (and
        (has_specified_activity_at ?room ?room_position)
    )
)

(:action detect_no_activity
    :parameters (?room - room ?room_position - room_position)
    :precondition (and
        (not (is_doing_read_at ?room ?room_position))
        (not (is_doing_sleep_at ?room ?room_position))
        (not (is_doing_bath_at ?room ?room_position))
    )
    :effect (and
        (not (has_specified_activity_at ?room ?room_position))
    )
)

; one check peer activity if it is fulfilled
(:action fulfill_activity_bath
    :parameters (?sensor - numerical_s ?room - room ?room_position - room_position)
    :precondition (or
        (sensor_is_part_of_room ?sensor ?room)
        (positioned_at ?sensor ?room_position)
        (is_doing_bath_at ?room ?room_position)
        (is_ok ?sensor)
    )
    :effect (and
        (fulfilled_activity ?room ?room_position)
    )
)

(:action fulfill_activity_read
    :parameters (?sensor - numerical_s ?room - room ?room_position - room_position)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (positioned_at ?sensor ?room_position)
        (is_doing_read_at ?room ?room_position)
        (is_ok ?sensor)
    )
    :effect (and
        (fulfilled_activity ?room ?room_position)
    )
)


(:action fulfill_activity_sleep
    :parameters (?sensor - numerical_s ?room - room ?room_position - room_position)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (positioned_at ?sensor ?room_position)
        (is_doing_sleep_at ?room ?room_position)
        (is_low ?sensor)
    )
    :effect (and
        (fulfilled_activity ?room ?room_position)
    )
)

(:action fulfill_no_activity
    :parameters (?room - room ?room_position - room_position)
    :precondition (and
        (not (has_specified_activity_at ?room ?room_position))
        (not (is_doing_read_at ?room ?room_position))
        (not (is_doing_sleep_at ?room ?room_position))
        (not (is_doing_bath_at ?room ?room_position))
    )
    :effect (and
        (fulfilled_activity ?room ?room_position)
    )
)

; optimisation for energy
; what if actuator of another room influences this sensor
(:action cancle_out_actuator
    :parameters (?sensor - numerical_s ?actuator_1 ?actuator_2 - actuator ?room - room)
    :precondition (and
        (not (= ?actuator_1 ?actuator_2))
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator_1 ?room)
        (actuator_is_part_of_room ?actuator_2 ?room)
        (actuator_increases_sensor ?actuator_1 ?sensor)
        (actuator_decreases_sensor ?actuator_2 ?sensor)
        (is_activated ?actuator_1)
        (is_activated ?actuator_2)
    )
    :effect (and
        (not (is_activated ?actuator_1))
        (not (is_activated ?actuator_2))

    )
)

(:action save_energy
    :parameters (?actuator - actuator ?room - room)
    :precondition (and
        (actuator_is_part_of_room ?actuator ?room)
        (not (is_ocupied ?room))
        (not (will_become_ocupied ?room))
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))

    )
)

)