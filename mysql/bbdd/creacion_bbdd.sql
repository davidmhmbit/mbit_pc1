USE Pictures;
CREATE TABLE pictures (
    id VARCHAR(36) NOT NULL,
    path VARCHAR(200) NOT NULL,
    size INTEGER NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
CREATE TABLE tags (
    tag VARCHAR(32) NOT NULL,
    picture_id VARCHAR(36) NOT NULL,
    confidence FLOAT NOT NULL,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
