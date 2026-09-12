/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle_acquire.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/06 18:30:00 by snaimi            #+#    #+#             */
/*   Updated: 2026/09/12 00:25:46 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	is_simulation_over(t_coder *coder)
{
	int	over;

	pthread_mutex_lock(&coder->data->state_mutex);
	over = coder->data->simulation_over;
	pthread_mutex_unlock(&coder->data->state_mutex);
	return (over);
}

void	get_priority_keys(t_coder *coder, long long *key, long long *seq)
{
	pthread_mutex_lock(&coder->data->state_mutex);
	if (coder->data->metrics.scheduler == SCHEDULER_EDF)
		*key = coder->last_compile_start + coder->data->metrics.time_to_burnout;
	else
		*key = coder->data->global_seq++;
	*seq = coder->data->global_seq++;
	pthread_mutex_unlock(&coder->data->state_mutex);
}

int	handle_single_coder(t_coder *coder, t_dongle *f)
{
	pthread_mutex_lock(&f->mutex);
	f->in_use = 1;
	pthread_mutex_unlock(&f->mutex);
	log_status(coder, "has taken a dongle");
	precise_sleep(coder->data->metrics.time_to_burnout + 10, coder->data);
	pthread_mutex_lock(&f->mutex);
	f->in_use = 0;
	pthread_mutex_unlock(&f->mutex);
	return (0);
}

int	try_grab_both(t_coder *coder, t_dongle *f, t_dongle *s)
{
	long long	now;

	now = get_time_ms();
	if (!f->in_use && now >= f->cooldown_until
		&& !s->in_use && now >= s->cooldown_until
		&& heap_peek(&f->queue) == coder
		&& heap_peek(&s->queue) == coder)
	{
		heap_pop(&f->queue);
		heap_pop(&s->queue);
		f->in_use = 1;
		s->in_use = 1;
		pthread_mutex_unlock(&s->mutex);
		pthread_mutex_unlock(&f->mutex);
		log_status(coder, "has taken a dongle");
		log_status(coder, "has taken a dongle");
		return (1);
	}
	return (0);
}
