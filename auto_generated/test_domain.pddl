(define (domain test_SCIoT_G02_2025)
    (:requirements :adl :strips :typing)
    (:types
        object_type - object
        cleaning_team_type floor_type iot_type room_position_type room_type - object_type
        actuator_type sensor_type - iot_type
        binary_a_type numerical_a_type textual_a_type - actuator_type
        light_switch_a_type switch_a_type virtual_switch_a_type - binary_a_type
        light_dimmer_a_type virtual_dimmer_a_type - numerical_a_type
        binary_s_type numerical_s_type textual_s_type - sensor_type
        button_s_type motion_s_type virtual_switch_s_type - binary_s_type
        humidity_s_type light_s_type rotation_s_type sound_s_type temperature_s_type virtual_dimmer_s_type - numerical_s_type
        display_a_type - textual_a_type
    )
    (:predicates (actuator_decreases_sensor ?actuator_type - actuator_type ?sensor_type - sensor_type)  (actuator_increases_sensor ?actuator_type - actuator_type ?sensor_type - sensor_type)  (actuator_is_part_of_room ?actuator_type - actuator_type ?room_type - room_type)  (checked_activity_bath ?room_type - room_type ?room_position_type - room_position_type)  (checked_activity_read ?room_type - room_type ?room_position_type - room_position_type)  (checked_activity_sleep ?room_type - room_type ?room_position_type - room_position_type)  (checked_activitys ?room_type - room_type ?room_position_type - room_position_type)  (fulfilled_activitys ?room_type - room_type ?room_position_type - room_position_type)  (is_activated ?actuator_type - actuator_type)  (is_at ?cleaning_team_type - cleaning_team_type ?room_type - room_type)  (is_cleaned ?room_type - room_type)  (is_doing_bath_at ?room_type - room_type ?room_position_type - room_position_type)  (is_doing_read_at ?room_type - room_type ?room_position_type - room_position_type)  (is_doing_sleep_at ?room_type - room_type ?room_position_type - room_position_type)  (is_high ?numerical_s_type - sensor_type)  (is_locked ?sensor_type - sensor_type)  (is_low ?numerical_s_type - sensor_type)  (is_next_to ?room_type - room_type ?room2_type - room_type)  (is_occupied ?room_type - room_type)  (is_ok ?numerical_s_type - sensor_type)  (is_sensing ?sensor_type - sensor_type)  (positioned_at ?iot_type - iot_type ?room_position_type - room_position_type)  (room_is_part_of_floor ?room_type - room_type ?floor_type - floor_type)  (sensor_is_part_of_room ?sensor_type - sensor_type ?room_type - room_type)  (will_become_occupied ?room_type - room_type))
    (:action assign_floor
        :parameters (?room_type - room_type ?floor_type - floor_type)
        :precondition (forall (?floor2_type - floor_type) (not (room_is_part_of_floor ?room_type ?floor2_type)))
        :effect (room_is_part_of_floor ?room_type ?floor_type)
    )
     (:action assign_room_position
        :parameters (?iot_type - iot_type)
        :precondition (forall (?room_position_type - room_position_type) (not (positioned_at ?iot_type ?room_position_type)))
        :effect (forall (?room_position_type - room_position_type) (positioned_at ?iot_type ?room_position_type))
    )
     (:action cancel_out_actuator
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?actuator2_type - actuator_type ?room_type - room_type)
        :precondition (and (not (= ?actuator_type ?actuator2_type)) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_increases_sensor ?actuator_type ?sensor_type) (actuator_decreases_sensor ?actuator2_type ?sensor_type) (is_activated ?actuator_type) (is_activated ?actuator2_type))
        :effect (and (is_activated ?actuator_type) (is_activated ?actuator2_type))
    )
     (:action decrease_s_by_a_in_r
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_decreases_sensor ?actuator_type ?sensor_type) (is_high ?sensor_type) (not (is_activated ?actuator_type)))
        :effect (and (not (is_high ?sensor_type)) (is_ok ?sensor_type) (is_activated ?actuator_type))
    )
     (:action decrease_s_by_na_in_r
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_increases_sensor ?actuator_type ?sensor_type) (is_high ?sensor_type) (is_activated ?actuator_type))
        :effect (and (not (is_high ?sensor_type)) (is_ok ?sensor_type) (not (is_activated ?actuator_type)))
    )
     (:action detect_activity_read
        :parameters (?binary_s_type - sensor_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (is_sensing ?binary_s_type) (positioned_at ?binary_s_type ?room_position_type) (sensor_is_part_of_room ?binary_s_type ?room_type) (not (checked_activity_read ?room_type ?room_position_type)))
        :effect (and (checked_activity_read ?room_type ?room_position_type) (is_doing_read_at ?room_type ?room_position_type))
    )
     (:action detect_activity_sleep
        :parameters (?binary_s_type - sensor_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (is_sensing ?binary_s_type) (positioned_at ?binary_s_type ?room_position_type) (sensor_is_part_of_room ?binary_s_type ?room_type) (not (checked_activity_sleep ?room_type ?room_position_type)))
        :effect (and (checked_activity_sleep ?room_type ?room_position_type) (is_doing_sleep_at ?room_type ?room_position_type))
    )
     (:action detect_all_activitys
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (checked_activity_sleep ?room_type ?room_position_type) (checked_activity_read ?room_type ?room_position_type) (not (checked_activitys ?room_type ?room_position_type)))
        :effect (checked_activitys ?room_type ?room_position_type)
    )
     (:action detect_no_activity_read
        :parameters (?binary_s_type - sensor_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_sensing ?binary_s_type)) (positioned_at ?binary_s_type ?room_position_type) (sensor_is_part_of_room ?binary_s_type ?room_type) (not (checked_activity_read ?room_type ?room_position_type)))
        :effect (and (checked_activity_read ?room_type ?room_position_type) (not (is_doing_read_at ?room_type ?room_position_type)))
    )
     (:action detect_no_activity_sleep
        :parameters (?binary_s_type - sensor_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_sensing ?binary_s_type)) (positioned_at ?binary_s_type ?room_position_type) (sensor_is_part_of_room ?binary_s_type ?room_type) (not (checked_activity_sleep ?room_type ?room_position_type)))
        :effect (and (checked_activity_sleep ?room_type ?room_position_type) (not (is_doing_sleep_at ?room_type ?room_position_type)))
    )
     (:action detect_no_possible_activity_read
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (exists (?binary_s_type - sensor_type) (and (positioned_at ?binary_s_type ?room_position_type) (sensor_is_part_of_room ?binary_s_type ?room_type)))) (not (checked_activity_read ?room_type ?room_position_type)))
        :effect (and (checked_activity_read ?room_type ?room_position_type) (not (is_doing_read_at ?room_type ?room_position_type)))
    )
     (:action detect_no_possible_activity_sleep
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (exists (?binary_s_type - sensor_type) (and (positioned_at ?binary_s_type ?room_position_type) (sensor_is_part_of_room ?binary_s_type ?room_type)))) (not (checked_activity_sleep ?room_type ?room_position_type)))
        :effect (and (checked_activity_sleep ?room_type ?room_position_type) (not (is_doing_sleep_at ?room_type ?room_position_type)))
    )
     (:action fulfill_activity_no_bath
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (checked_activitys ?room_type ?room_position_type) (not (is_doing_bath_at ?room_type ?room_position_type)) (not (checked_activity_bath ?room_type ?room_position_type)))
        :effect (checked_activity_bath ?room_type ?room_position_type)
    )
     (:action fulfill_activity_no_read
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (checked_activitys ?room_type ?room_position_type) (not (is_doing_read_at ?room_type ?room_position_type)) (not (checked_activity_read ?room_type ?room_position_type)))
        :effect (checked_activity_read ?room_type ?room_position_type)
    )
     (:action fulfill_activity_no_sleep
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (checked_activitys ?room_type ?room_position_type) (not (is_doing_sleep_at ?room_type ?room_position_type)) (not (checked_activity_sleep ?room_type ?room_position_type)))
        :effect (checked_activity_sleep ?room_type ?room_position_type)
    )
     (:action fulfill_activity_read
        :parameters (?sensor_type - sensor_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (checked_activitys ?room_type ?room_position_type) (is_doing_read_at ?room_type ?room_position_type) (not (checked_activity_read ?room_type ?room_position_type)) (is_high ?sensor_type))
        :effect (and (checked_activity_read ?room_type ?room_position_type) (is_locked ?sensor_type))
    )
     (:action fulfill_activity_sleep
        :parameters (?sensor_type - sensor_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (checked_activitys ?room_type ?room_position_type) (is_doing_sleep_at ?room_type ?room_position_type) (not (checked_activity_sleep ?room_type ?room_position_type)) (is_low ?sensor_type))
        :effect (and (checked_activity_sleep ?room_type ?room_position_type) (is_locked ?sensor_type))
    )
     (:action fulfill_all_activitys
        :parameters (?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (checked_activitys ?room_type ?room_position_type) (checked_activity_sleep ?room_type ?room_position_type) (checked_activity_read ?room_type ?room_position_type) (not (fulfilled_activitys ?room_type ?room_position_type)))
        :effect (fulfilled_activitys ?room_type ?room_position_type)
    )
     (:action increase_s_by_a_in_r
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_increases_sensor ?actuator_type ?sensor_type) (is_low ?sensor_type) (not (is_activated ?actuator_type)))
        :effect (and (not (is_low ?sensor_type)) (is_ok ?sensor_type) (is_activated ?actuator_type))
    )
     (:action increase_s_by_na_in_r
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_decreases_sensor ?actuator_type ?sensor_type) (is_low ?sensor_type) (is_activated ?actuator_type))
        :effect (and (not (is_low ?sensor_type)) (is_ok ?sensor_type) (not (is_activated ?actuator_type)))
    )
     (:action move_to_floor
        :parameters (?cleaning_team_type - cleaning_team_type ?room_type - room_type ?room2_type - room_type ?floor_type - floor_type ?floor2_type - floor_type)
        :precondition (and (is_at ?cleaning_team_type ?room_type) (or (is_next_to ?room_type ?room2_type) (is_next_to ?room2_type ?room_type)) (room_is_part_of_floor ?room_type ?floor_type) (room_is_part_of_floor ?room2_type ?floor2_type) (not (= ?floor_type ?floor2_type)))
        :effect (and (not (is_at ?cleaning_team_type ?room_type)) (is_at ?cleaning_team_type ?room2_type))
    )
     (:action move_to_isolated_room
        :parameters (?cleaning_team_type - cleaning_team_type ?room_type - room_type ?room2_type - room_type ?floor_type - floor_type)
        :precondition (and (is_at ?cleaning_team_type ?room_type) (forall (?room3_type - room_type) (and (not (is_next_to ?room3_type ?room2_type)) (not (is_next_to ?room2_type ?room3_type)))) (room_is_part_of_floor ?room_type ?floor_type) (room_is_part_of_floor ?room2_type ?floor_type))
        :effect (and (not (is_at ?cleaning_team_type ?room_type)) (is_at ?cleaning_team_type ?room2_type))
    )
     (:action move_to_room
        :parameters (?cleaning_team_type - cleaning_team_type ?room_type - room_type ?room2_type - room_type ?floor_type - floor_type)
        :precondition (and (is_at ?cleaning_team_type ?room_type) (or (is_next_to ?room_type ?room2_type) (is_next_to ?room2_type ?room_type)) (room_is_part_of_floor ?room_type ?floor_type) (room_is_part_of_floor ?room2_type ?floor_type))
        :effect (and (not (is_at ?cleaning_team_type ?room_type)) (is_at ?cleaning_team_type ?room2_type))
    )
     (:action save_energy
        :parameters (?actuator_type - actuator_type ?room_type - room_type)
        :precondition (and (actuator_is_part_of_room ?actuator_type ?room_type) (not (is_occupied ?room_type)) (not (will_become_occupied ?room_type)) (is_activated ?actuator_type))
        :effect (not (is_activated ?actuator_type))
    )
     (:action team_clean
        :parameters (?cleaning_team_type - cleaning_team_type ?room_type - room_type)
        :precondition (and (is_at ?cleaning_team_type ?room_type) (not (is_cleaned ?room_type)) (not (is_occupied ?room_type)) (not (will_become_occupied ?room_type)))
        :effect (is_cleaned ?room_type)
    )
     (:action turn_off
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_increases_sensor ?actuator_type ?sensor_type) (is_sensing ?sensor_type) (is_activated ?actuator_type))
        :effect (and (not (is_sensing ?sensor_type)) (not (is_activated ?actuator_type)))
    )
     (:action turn_off_inverted
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_decreases_sensor ?actuator_type ?sensor_type) (is_sensing ?sensor_type) (not (is_activated ?actuator_type)))
        :effect (and (not (is_sensing ?sensor_type)) (is_activated ?actuator_type))
    )
     (:action turn_on
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_increases_sensor ?actuator_type ?sensor_type) (not (is_sensing ?sensor_type)) (not (is_activated ?actuator_type)))
        :effect (and (is_sensing ?sensor_type) (is_activated ?actuator_type))
    )
     (:action turn_on_inverted
        :parameters (?sensor_type - sensor_type ?actuator_type - actuator_type ?room_type - room_type ?room_position_type - room_position_type)
        :precondition (and (not (is_locked ?sensor_type)) (positioned_at ?sensor_type ?room_position_type) (sensor_is_part_of_room ?sensor_type ?room_type) (actuator_decreases_sensor ?actuator_type ?sensor_type) (not (is_sensing ?sensor_type)) (is_activated ?actuator_type))
        :effect (and (is_sensing ?sensor_type) (not (is_activated ?actuator_type)))
    )
)