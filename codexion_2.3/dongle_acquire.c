/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle_acquire.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/06 18:30:00 by snaimi            #+#    #+#             */
/*   Updated: 2026/09/06 18:06:08 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	try_grab_dongle(t_coder *coder, t_dongle *dongle)
{
	pthread_mutex_lock(&coder->data->state_mutex);
	if (coder->data->simulation_over)
	{
		pthread_mutex_unlock(&coder->data->state_mutex);
		pthread_mutex_unlock(&dongle->mutex);
		return (0);
	}
	pthread_mutex_unlock(&coder->data->state_mutex);
	if (!dongle->in_use && get_time_ms() >= dongle->cooldown_until
		&& heap_peek(&dongle->queue) == coder)
	{
		heap_pop(&dongle->queue);
		dongle->in_use = 1;
		pthread_mutex_unlock(&dongle->mutex);
		log_status(coder, "has taken a dongle");
		return (1);
	}
	return (-1);
}

int	acquire_one_dongle(t_coder *coder, t_dongle *dongle)
{
	long long	key;
	long long	seq;
	int			status;

	pthread_mutex_lock(&dongle->mutex);
	pthread_mutex_lock(&coder->data->state_mutex);
	if (coder->data->metrics.scheduler == SCHEDULER_EDF)
		key = coder->last_compile_start + coder->data->metrics.time_to_burnout;
	else
		key = coder->data->global_seq++;
	seq = coder->data->global_seq++;
	pthread_mutex_unlock(&coder->data->state_mutex);
	heap_push(&dongle->queue, coder, key, seq);
	while (1)
	{
		status = try_grab_dongle(coder, dongle);
		if (status != -1)
			return (status);
		pthread_cond_wait(&dongle->cond, &dongle->mutex);
	}
}
