/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   routines.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 09:54:15 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

void	log_status(t_coder *coder, const char *status)
{
	long long	timestamp;

	pthread_mutex_lock(&coder->data->state_mutex);
	if (!coder->data->simulation_over)
	{
		pthread_mutex_lock(&coder->data->write_mutex);
		timestamp = get_time_ms() - coder->data->start_time;
		printf("%lld %d %s\n", timestamp, coder->id, status);
		pthread_mutex_unlock(&coder->data->write_mutex);
	}
	pthread_mutex_unlock(&coder->data->state_mutex);
}

static int	should_stop(t_coder *coder)
{
	int	stop;

	pthread_mutex_lock(&coder->data->state_mutex);
	stop = coder->data->simulation_over;
	pthread_mutex_unlock(&coder->data->state_mutex);
	return (stop);
}

static int	compile_step(t_coder *coder)
{
	if (!take_dongles(coder))
		return (0);
	pthread_mutex_lock(&coder->data->state_mutex);
	coder->last_compile_start = get_time_ms();
	coder->compiles_done++;
	pthread_mutex_unlock(&coder->data->state_mutex);
	log_status(coder, "is compiling");
	precise_sleep(coder->data->metrics.time_to_compile, coder->data);
	release_dongles(coder);
	return (1);
}

void	*coder_routine(void *arg)
{
	t_coder	*coder;

	coder = (t_coder *)arg;
	if (coder->id % 2 == 0)
		precise_sleep(1, coder->data);
	while (!should_stop(coder))
	{
		if (!compile_step(coder) || should_stop(coder))
			break ;
		log_status(coder, "is debugging");
		precise_sleep(coder->data->metrics.time_to_debug, coder->data);
		if (should_stop(coder))
			break ;
		log_status(coder, "is refactoring");
		precise_sleep(coder->data->metrics.time_to_refactor, coder->data);
	}
	return (NULL);
}