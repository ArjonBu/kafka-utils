Feature: kafka_consumer_manager offset_save subcommand

 # This may fail TODO remove
  Scenario: Calling the offset_save command after consuming some messages
     Given we have an existing kafka cluster with a topic
     Given we have initialized kafka offsets storage
      when we produce some number of messages into the topic
      when we consume some number of messages from the topic
      when we call the offset_save command with an offsets file
      then the correct offsets will be saved into the given file

  Scenario: Calling offset_save after offset_restore
     Given we have an existing kafka cluster with a topic
     Given we have initialized kafka offsets storage
      when we produce some number of messages into the topic
      when we consume some number of messages from the topic
     Given we have a json offsets file
      when we call the offset_restore command with the offsets file
      when we call the offset_save command with an offsets file
      then the restored offsets will be saved into the given file
