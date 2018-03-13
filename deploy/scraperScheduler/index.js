const AWS = require('aws-sdk');
const ecs = new AWS.ECS();

const fs = require('fs');
const spiders = fs.readFileSync('./spiders.txt', {encoding: 'utf-8'});

const tasks = spiders.trim().split("\n").sort();

if (tasks.length > 48) {
  throw "Too many tasks defined!";
}

exports.handler = (events, context) => {
    const now = new Date();
    const hour = now.getHours();
    const task = tasks[hour];

    if (!task) {
        console.log(`no task for index ${hour}; we're done here.`)
        return;
    }

    const params = {
        taskDefinition: `documenters_aggregator-${task}`,
        cluster: 'documenters-aggregator-production',
        count: 1
    };
    ecs.runTask(params, (err, data) => {
        if (err) {
            console.log(err, err.stack);
        } else {
            console.log(data);
        }
        context.done(err, data);
    });
};
