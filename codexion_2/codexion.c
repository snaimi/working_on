/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   codexion.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 09:53:21 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	init_coders(t_data *data)
{
	int	i;

	i = 0;
	while (i < data->metrics.number_of_coders)
	{
		data->coders[i].id = i + 1;
		data->coders[i].compiles_done = 0;
		data->coders[i].data = data;
		data->coders[i].left_dongle = &data->dongles[i];
		data->coders[i].right_dongle = &data->dongles[(i + 1)
			% data->metrics.number_of_coders];
		i++;
	}
}

static int	init_data(t_data *data, int argc, char **argv)
{
	if (!parse_arguments(argc, argv, &data->metrics))
	{
		printf("Error: Invalid arguments\n");
		return (0);
	}
	data->simulation_over = 0;
	pthread_mutex_init(&data->write_mutex, NULL);
	pthread_mutex_init(&data->state_mutex, NULL);
	init_dongles(data);
	data->coders = malloc(sizeof(t_coder) * data->metrics.number_of_coders);
	if (!data->coders || !data->dongles)
		return (0);
	init_coders(data);
	return (1);
}

static void	clean_exit(t_data *data)
{
	int	i;

	i = 0;
	while (i < data->metrics.number_of_coders)
	{
		pthread_join(data->coders[i].thread, NULL);
		i++;
	}
	pthread_join(data->monitor_thread, NULL);
	destroy_dongles(data);
	pthread_mutex_destroy(&data->write_mutex);
	pthread_mutex_destroy(&data->state_mutex);
	free(data->coders);
}

int	main(int argc, char **argv)
{
	t_data	data;
	int		i;

	if (!init_data(&data, argc, argv))
		return (1);
	data.start_time = get_time_ms();
	i = 0;
	while (i < data.metrics.number_of_coders)
	{
		data.coders[i].last_compile_start = data.start_time;
		pthread_create(&data.coders[i].thread, NULL, coder_routine,
			&data.coders[i]);
		i++;
	}
	pthread_create(&data.monitor_thread, NULL, monitor_routine, &data);
	clean_exit(&data);
	return (0);
}