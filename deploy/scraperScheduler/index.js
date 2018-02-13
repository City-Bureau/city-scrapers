const AWS = require('aws-sdk')
const ecs = new AWS.ECS();

const tasks = [
    'chi_animal',
    'chi_buildings',
    'chi_city_college',
    'chi_citycouncil',
    'chi_infra',
    'chi_library',
    'chi_parks',
    'chi_police',
    'chi_policeboard',
    'chi_pubhealth',
    'chi_school_actions',
    'chi_schools',
    'chi_transit',
    'cook_board',
    'cook_county',
    'cook_electoral',
    'cook_hospitals',
    'cook_landbank',
    'cook_pubhealth',
    'il_labor',
    'il_pubhealth',
    'regionaltransit',
    'ward_night',
];

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
