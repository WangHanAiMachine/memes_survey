DROP TABLE IF EXISTS questionsStatus;

CREATE TABLE questionsStatus (
    modelId INTEGER,
    contextId INTEGER,
    memeId INTEGER,
    annotationId INTEGER,
    userId INTEGER,
    annotated INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (modelId, contextId, memeId, annotationId)
);


DROP TABLE IF EXISTS inprogress;

CREATE TABLE inprogress (
    modelId INTEGER,
    contextId INTEGER,
    memeId INTEGER,
    annotationId INTEGER,
    startTime INTEGER NOT NULL,
    PRIMARY KEY (modelId, contextId, memeId, annotationId)

);


DROP TABLE IF EXISTS submitted;

CREATE TABLE submitted (
    modelId INTEGER,
    contextId INTEGER,
    memeId INTEGER,
    annotationId INTEGER,
    startTime TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    hilarity_text INTEGER,
    support_text TEXT,
    similar_meme TEXT,
    hateful_meme TEXT,
    hilarity_meme INTEGER,
    support_meme TEXT,
    persuasiveness  INTEGER,
    PRIMARY KEY (modelId, contextId, memeId, annotationId)
);

