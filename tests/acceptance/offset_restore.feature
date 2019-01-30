Feature: kafka_consumer_manager offset_restore subcommand

    # TODO: check if it passes
  Scenario: Calling the offset_restore command
     Given we have an existing kafka cluster with a topic
     Given we have initialized kafka offsets storage
      when we produce some number of messages into the topic
      when we consume some number of messages from the topic
     Given we have a json offsets file
      when we call the offset_restore command with the offsets file
      then the committed offsets will match the offsets file
