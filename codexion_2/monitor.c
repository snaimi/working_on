/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   monitor.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 09:54:01 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	stop_due_to_burnout(t_data *data, int id, long long ts)
{
	data->simulation_over = 1;
	pthread_mutex_lock(&data->write_mutex);
	printf("%lld %d burned out\n", ts - data->start_time, id);
	pthread_mutex_unlock(&data->write_mutex);
	pthread_mutex_unlock(&data->state_mutex);
}

static int	check_all_compiles_completed(t_data *data)
{
	int	i;

	if (data->metrics.number_of_compiles_required == -1)
		return (0);
	i = 0;
	while (i < data->metrics.number_of_coders)
	{
		if (data->coders[i].compiles_done
			< data->metrics.number_of_compiles_required)
			return (0);
		i++;
	}
	return (1);
}

static int	check_burnout(t_data *data)
{
	int			i;
	long long	now;

	now = get_time_ms();
	i = 0;
	while (i < data->metrics.number_of_coders)
	{
		if ((now - data->coders[i].last_compile_start)
			>= data->metrics.time_to_burnout)
		{
			stop_due_to_burnout(data, data->coders[i].id, now);
			return (1);
		}
		i++;
	}
	return (0);
}

void	*monitor_routine(void *arg)
{
	t_data	*data;

	data = (t_data *)arg;
	while (1)
	{
		pthread_mutex_lock(&data->state_mutex);
		if (data->simulation_over)
		{
			pthread_mutex_unlock(&data->state_mutex);
			break ;
		}
		if (check_all_compiles_completed(data))
		{
			data->simulation_over = 1;
			pthread_mutex_unlock(&data->state_mutex);
			break ;
		}
		if (check_burnout(data))
			return (NULL);
		pthread_mutex_unlock(&data->state_mutex);
		usleep(500);
	}
	return (NULL);
}